/**
 * Script de Resguardo Automatizado de Base de Datos Firestore para ElectroFrío
 * Descarga el 100% de las colecciones de datos y las guarda en backups/datos_semanales/
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const readline = require('readline');

// Configuración de Firebase del Proyecto
const FIREBASE_CONFIG = {
    apiKey: "AIzaSyAHtMvkoHg2-OQaLOZ1Jvlsp6Bi3_-LP-s",
    projectId: "electrofriov2",
    authDomain: "electrofriov2.firebaseapp.com"
};

const COLLECTIONS = [
    'clientes',
    'ordenes',
    'ordenesTrabajo',
    'planillas',
    'planillasDigitales',
    'presupuestos',
    'materiales',
    'mano_obra',
    'cobros_movimientos',
    'tareas',
    'fichajes',
    'usuarios',
    'configuracion'
];

function formatEmail(input) {
    if (input.includes('@')) return input;
    return `${input}@electrofrio.com`;
}

// Función auxiliar para peticiones HTTP
function httpRequest(options, postData) {
    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(parsed);
                    } else {
                        reject(new Error(parsed.error?.message || `HTTP ${res.statusCode}: ${data}`));
                    }
                } catch (e) {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(data);
                    } else {
                        reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                    }
                }
            });
        });

        req.on('error', (err) => reject(err));
        if (postData) {
            req.write(postData);
        }
        req.end();
    });
}

// Iniciar sesión con Firebase Auth REST API
async function signInFirebaseAuth(email, password) {
    const postData = JSON.stringify({
        email: formatEmail(email),
        password: password,
        returnSecureToken: true
    });

    const options = {
        hostname: 'identitytoolkit.googleapis.com',
        path: `/v1/accounts:signInWithPassword?key=${FIREBASE_CONFIG.apiKey}`,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    const res = await httpRequest(options, postData);
    return res.idToken;
}

// Convertidor de formato de documento Firestore REST a JSON plano
function parseFirestoreValue(fieldVal) {
    if (!fieldVal || typeof fieldVal !== 'object') return fieldVal;
    if ('stringValue' in fieldVal) return fieldVal.stringValue;
    if ('integerValue' in fieldVal) return parseInt(fieldVal.integerValue, 10);
    if ('doubleValue' in fieldVal) return parseFloat(fieldVal.doubleValue);
    if ('booleanValue' in fieldVal) return fieldVal.booleanValue;
    if ('timestampValue' in fieldVal) return fieldVal.timestampValue;
    if ('nullValue' in fieldVal) return null;
    if ('mapValue' in fieldVal) {
        const res = {};
        const fields = fieldVal.mapValue.fields || {};
        for (const k in fields) {
            res[k] = parseFirestoreValue(fields[k]);
        }
        return res;
    }
    if ('arrayValue' in fieldVal) {
        const list = fieldVal.arrayValue.values || [];
        return list.map(parseFirestoreValue);
    }
    return fieldVal;
}

function parseFirestoreDocument(doc) {
    const data = {};
    const fields = doc.fields || {};
    for (const k in fields) {
        data[k] = parseFirestoreValue(fields[k]);
    }
    return data;
}

// Función principal de Backup
async function runBackup() {
    console.log("=================================================");
    console.log("   ELECTROFRÍO - RESPALDO AUTOMÁTICO DE DATOS   ");
    console.log("=================================================");
    console.log(`Iniciando a las: ${new Date().toLocaleString('es-AR')}`);

    const backupDir = path.join(__dirname, 'backups', 'datos_semanales');
    if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
    }

    const backupData = {
        metadata: {
            version: "2.0",
            system: "ElectroFrío Refrigeración",
            generatedAt: new Date().toISOString(),
            timestamp: Date.now(),
            projectId: FIREBASE_CONFIG.projectId,
            source: "Windows Scheduled / CLI Task"
        },
        collections: {},
        totalDocuments: 0,
        stats: {}
    };

    let totalDocs = 0;
    const serviceAccountPath = path.join(__dirname, 'serviceAccountKey.json');
    const configCredentialsPath = path.join(__dirname, 'backup_credentials.json');

    // 1. Probar con Firebase Admin SDK si existe archivo de servicio
    if (fs.existsSync(serviceAccountPath)) {
        console.log("→ Detectado serviceAccountKey.json. Usando Firebase Admin SDK con acceso total...");
        try {
            const admin = require('firebase-admin');
            if (!admin.apps.length) {
                const serviceAccount = require(serviceAccountPath);
                admin.initializeApp({
                    credential: admin.credential.cert(serviceAccount)
                });
            }
            const db = admin.firestore();

            for (const col of COLLECTIONS) {
                process.stdout.write(`  Descargando colección '${col}'... `);
                const snapshot = await db.collection(col).get();
                backupData.collections[col] = {};
                let count = 0;

                snapshot.forEach(doc => {
                    backupData.collections[col][doc.id] = doc.data();
                    count++;
                });

                backupData.stats[col] = count;
                totalDocs += count;
                console.log(`✓ (${count} docs)`);
            }
        } catch (adminErr) {
            console.error("Error al usar Firebase Admin SDK:", adminErr.message);
        }
    } else {
        // 2. Usar Firebase Auth REST API
        let idToken = null;

        // Verificar si existen credenciales en backup_credentials.json o variables de entorno
        let user = process.env.ELECTROFRIO_USER;
        let pass = process.env.ELECTROFRIO_PASS;

        if (fs.existsSync(configCredentialsPath)) {
            try {
                const creds = JSON.parse(fs.readFileSync(configCredentialsPath, 'utf-8'));
                user = user || creds.user || creds.email || creds.username;
                pass = pass || creds.pass || creds.password;
            } catch (e) { }
        }

        if (user && pass) {
            console.log(`→ Autenticando como '${user}' mediante Firebase Auth...`);
            try {
                idToken = await signInFirebaseAuth(user, pass);
                console.log("✓ Autenticación exitosa.");
            } catch (authErr) {
                console.warn("⚠️ No se pudo autenticar con las credenciales guardadas:", authErr.message);
            }
        }

        console.log("→ Descargando colecciones de Firestore...");
        for (const col of COLLECTIONS) {
            process.stdout.write(`  Descargando colección '${col}'... `);
            backupData.collections[col] = {};
            let count = 0;
            let pageToken = null;

            try {
                do {
                    const tokenParam = pageToken ? `&pageToken=${encodeURIComponent(pageToken)}` : '';
                    const headers = { 'Accept': 'application/json' };
                    if (idToken) {
                        headers['Authorization'] = `Bearer ${idToken}`;
                    }

                    const options = {
                        hostname: 'firestore.googleapis.com',
                        path: `/v1/projects/${FIREBASE_CONFIG.projectId}/databases/(default)/documents/${col}?pageSize=300${tokenParam}&key=${FIREBASE_CONFIG.apiKey}`,
                        method: 'GET',
                        headers: headers
                    };

                    const res = await httpRequest(options);
                    const docs = res.documents || [];

                    for (const doc of docs) {
                        const parts = doc.name.split('/');
                        const docId = parts[parts.length - 1];
                        backupData.collections[col][docId] = parseFirestoreDocument(doc);
                        count++;
                    }

                    pageToken = res.nextPageToken;
                } while (pageToken);

                backupData.stats[col] = count;
                totalDocs += count;
                console.log(`✓ (${count} docs)`);
            } catch (err) {
                console.log(`⚠️ (Aviso: ${err.message})`);
                backupData.stats[col] = `Error: ${err.message}`;
            }
        }
    }

    backupData.totalDocuments = totalDocs;

    // Guardar archivo JSON
    const dateStr = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const fileName = `backup_electrofrio_${dateStr}.json`;
    const filePath = path.join(backupDir, fileName);

    fs.writeFileSync(filePath, JSON.stringify(backupData, null, 2), 'utf-8');
    const fileSizeMB = (fs.statSync(filePath).size / (1024 * 1024)).toFixed(2);

    console.log("=================================================");
    console.log("   ¡COPIA DE SEGURIDAD COMPLETADA EXITOSAMENTE!  ");
    console.log("=================================================");
    console.log(`Archivo generado: ${fileName}`);
    console.log(`Ubicación:        ${filePath}`);
    console.log(`Total documentos: ${totalDocs}`);
    console.log(`Tamaño:           ${fileSizeMB} MB`);
    console.log("=================================================");

    // Limpieza de backups antiguos (mantener últimos 52 semanales = 1 año)
    try {
        const files = fs.readdirSync(backupDir)
            .filter(f => f.startsWith('backup_electrofrio_') && f.endsWith('.json'))
            .map(f => ({ name: f, time: fs.statSync(path.join(backupDir, f)).mtime.getTime() }))
            .sort((a, b) => b.time - a.time);

        if (files.length > 52) {
            const toDelete = files.slice(52);
            toDelete.forEach(f => {
                fs.unlinkSync(path.join(backupDir, f.name));
                console.log(`Rotación: eliminado backup antiguo ${f.name}`);
            });
        }
    } catch (e) {
        // ignorar error de rotación
    }
}

runBackup().catch(err => {
    console.error("Error fatal en el respaldo:", err);
    process.exit(1);
});
