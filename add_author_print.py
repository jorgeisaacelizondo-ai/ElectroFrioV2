import re

filepath = "c:\\Users\\PC\\Desktop\\Dev\\ElectroFrioV2\\index.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Change badge color to green
content = content.replace(
    '''<td data-label="AUTOR"><span style="color: #ff4444; font-weight: bold; background: rgba(255,68,68,0.1); padding: 4px 8px; border-radius: 4px; font-size: 11px; display: inline-block;">${p.cargado_por || 'Sin registrar'}</span></td>''',
    '''<td data-label="AUTOR"><span style="color: #4caf50; font-weight: bold; background: rgba(76,175,80,0.1); padding: 4px 8px; border-radius: 4px; font-size: 11px; display: inline-block;">${p.cargado_por || 'Sin registrar'}</span></td>'''
)

# 2. Add Author to print view
content = content.replace(
    '''                            <div><div class="label">Técnicos / Colaboradores Intervinientes</div><div class="val">${techs} (${numCollabs})</div></div>
                        </div>''',
    '''                            <div><div class="label">Técnicos / Colaboradores Intervinientes</div><div class="val">${techs} (${numCollabs})</div></div>
                            <div><div class="label">Planilla Cargada Por (Autor)</div><div class="val">${p.cargado_por || 'Sin registrar'}</div></div>
                        </div>'''
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch 4 done")
