/**
 * ====================================================================
 * ELECTROFRÍO - MODO SEGURO / SANDBOX LOCAL
 * ====================================================================
 * Protege la base de datos real en la nube (Firestore) cuando se ejecuta
 * la aplicación en entorno de desarrollo local (localhost / 127.0.0.1).
 *
 * - Permite lectura completa (visualizar clientes, presupuestos, etc.)
 * - Intercepta y bloquea operaciones de escritura (add, set, update, delete, batch)
 * - Simula respuestas exitosas para evitar que la interfaz falle
 * - Totalmente inerte en producción (electrofriov2.web.app)
 * ====================================================================
 */

(function () {
    const isLocalhost = window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1' ||
                        window.location.hostname === '';

    // Si no está en localhost, no aplicar ninguna restricción
    if (!isLocalhost) {
        return;
    }

    const STORAGE_KEY = 'ELECTROFRIO_MODO_SEGURO';

    // Por defecto DESACTIVADO: las operaciones impactan en la base de datos real de Cloud Firestore
    let modoSeguroActivo = localStorage.getItem(STORAGE_KEY) === 'true';

    console.info(`%c🛡️ [MODO SEGURO] Activo: ${modoSeguroActivo} (Entorno Localhost - Escrituras Reales: ${!modoSeguroActivo})`, 
        'background: #1e3656; color: #4cd964; font-weight: bold; padding: 4px 8px; border-radius: 4px;');

    function mostrarAvisoEscritura(accion, path) {
        const msg = `🛡️ [Modo Seguro] Operación '${accion}' prevenida en '${path || 'colección'}'. La base de datos real NO fue modificada.`;
        console.warn(msg);
        if (typeof window.showToast === 'function') {
            window.showToast(msg, 'warning');
        }
    }

    // Interceptar Firestore una vez que la librería esté cargada
    function inicializarInterceptores() {
        if (!window.firebase || !window.firebase.firestore) {
            setTimeout(inicializarInterceptores, 50);
            return;
        }

        const firestore = window.firebase.firestore;

        // Guardar métodos originales
        const origAdd = firestore.CollectionReference.prototype.add;
        const origSet = firestore.DocumentReference.prototype.set;
        const origUpdate = firestore.DocumentReference.prototype.update;
        const origDelete = firestore.DocumentReference.prototype.delete;
        const origBatchCommit = firestore.WriteBatch ? firestore.WriteBatch.prototype.commit : null;

        // 1. Interceptar CollectionReference.add
        firestore.CollectionReference.prototype.add = function (data) {
            if (!modoSeguroActivo) return origAdd.apply(this, arguments);
            const path = this.path;
            mostrarAvisoEscritura('Crear documento (add)', path);

            // Devolver una referencia simulada para que código que use const doc = await col.add(...) no falle
            const fakeId = 'mock_' + Math.random().toString(36).substr(2, 9);
            const fakeDocRef = this.doc(fakeId);
            return Promise.resolve(fakeDocRef);
        };

        // 2. Interceptar DocumentReference.set
        firestore.DocumentReference.prototype.set = function (data, options) {
            if (!modoSeguroActivo) return origSet.apply(this, arguments);
            mostrarAvisoEscritura('Guardar (set)', this.path);
            return Promise.resolve();
        };

        // 3. Interceptar DocumentReference.update
        firestore.DocumentReference.prototype.update = function () {
            if (!modoSeguroActivo) return origUpdate.apply(this, arguments);
            mostrarAvisoEscritura('Actualizar (update)', this.path);
            return Promise.resolve();
        };

        // 4. Interceptar DocumentReference.delete
        firestore.DocumentReference.prototype.delete = function () {
            if (!modoSeguroActivo) return origDelete.apply(this, arguments);
            mostrarAvisoEscritura('Eliminar (delete)', this.path);
            return Promise.resolve();
        };

        // 5. Interceptar WriteBatch.commit
        if (origBatchCommit) {
            firestore.WriteBatch.prototype.commit = function () {
                if (!modoSeguroActivo) return origBatchCommit.apply(this, arguments);
                mostrarAvisoEscritura('Lote de escrituras (batch.commit)', 'múltiples documentos');
                return Promise.resolve();
            };
        }

        // 6. Interceptar Transaction
        if (firestore.Transaction) {
            const origTransSet = firestore.Transaction.prototype.set;
            const origTransUpdate = firestore.Transaction.prototype.update;
            const origTransDelete = firestore.Transaction.prototype.delete;

            firestore.Transaction.prototype.set = function () {
                if (!modoSeguroActivo) return origTransSet.apply(this, arguments);
                mostrarAvisoEscritura('Transacción (set)', arguments[0]?.path);
                return this;
            };
            firestore.Transaction.prototype.update = function () {
                if (!modoSeguroActivo) return origTransUpdate.apply(this, arguments);
                mostrarAvisoEscritura('Transacción (update)', arguments[0]?.path);
                return this;
            };
            firestore.Transaction.prototype.delete = function () {
                if (!modoSeguroActivo) return origTransDelete.apply(this, arguments);
                mostrarAvisoEscritura('Transacción (delete)', arguments[0]?.path);
                return this;
            };
        }

        crearIndicadorVisual();
    }

    function crearIndicadorVisual() {
        // No duplicar indicador si ya existe (o si es un iframe hijo)
        if (document.getElementById('modo-seguro-badge') || window.self !== window.top) {
            return;
        }

        const badge = document.createElement('div');
        badge.id = 'modo-seguro-badge';
        badge.style.position = 'fixed';
        badge.style.bottom = '16px';
        badge.style.right = '16px';
        badge.style.zIndex = '999999';
        badge.style.display = 'flex';
        badge.style.alignItems = 'center';
        badge.style.gap = '8px';
        badge.style.padding = '8px 14px';
        badge.style.borderRadius = '30px';
        badge.style.fontSize = '12px';
        badge.style.fontWeight = '600';
        badge.style.fontFamily = "'Inter', sans-serif";
        badge.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
        badge.style.transition = 'all 0.3s ease';
        badge.style.cursor = 'pointer';

        function actualizarEstilo() {
            if (modoSeguroActivo) {
                badge.style.backgroundColor = '#382b0e';
                badge.style.color = '#f1c40f';
                badge.style.border = '1px solid #f39c12';
                badge.innerHTML = `🛡️ <span>Modo Seguro: <strong>ACTIVADO</strong> (Escrituras bloqueadas)</span>`;
                badge.title = "Las escrituras a la base de datos están bloqueadas. Haz clic para activar escrituras reales.";
            } else {
                badge.style.backgroundColor = '#0b3d20';
                badge.style.color = '#4cd964';
                badge.style.border = '1px solid #2ecc71';
                badge.innerHTML = `🟢 <span>Firestore Real: <strong>CONECTADO</strong> (Escrituras activas)</span>`;
                badge.title = "Las altas, ediciones y fichajes impactan en la base real de Cloud Firestore. Haz clic para activar Modo Seguro si deseas bloquearlas.";
            }
        }

        badge.addEventListener('click', () => {
            modoSeguroActivo = !modoSeguroActivo;
            localStorage.setItem(STORAGE_KEY, modoSeguroActivo ? 'true' : 'false');
            actualizarEstilo();
            if (typeof window.showToast === 'function') {
                window.showToast(
                    modoSeguroActivo
                        ? '🛡️ Modo Seguro ACTIVADO: Las escrituras en Firestore están bloqueadas'
                        : '🟢 Firestore Real CONECTADO: Las operaciones se guardan en la base real',
                    modoSeguroActivo ? 'warning' : 'success'
                );
            }
        });

        actualizarEstilo();

        if (document.body) {
            document.body.appendChild(badge);
        } else {
            document.addEventListener('DOMContentLoaded', () => document.body.appendChild(badge));
        }
    }

    // Exponer API global por si se necesita controlar programáticamente
    window.ModoSeguro = {
        isActivo: () => modoSeguroActivo,
        activar: () => {
            modoSeguroActivo = true;
            localStorage.setItem(STORAGE_KEY, 'true');
        },
        desactivar: () => {
            modoSeguroActivo = false;
            localStorage.setItem(STORAGE_KEY, 'false');
        }
    };

    inicializarInterceptores();
})();
