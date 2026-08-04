import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# For admin array
c = re.sub(r'(if \(role === \'Administrador\'\) \{\s*visibleAndOrdered = \[\s*itemDashboard,\s*itemOrdenes,)',
           r'\1\n                          itemTareas,', c)

# For premium array
c = re.sub(r'(} else if \(isPremium\) \{\s*visibleAndOrdered = \[\s*itemDashboard,\s*itemOrdenes,)',
           r'\1\n                          itemTareas,', c)

# For collab array
c = re.sub(r'(} else \{\s*visibleAndOrdered = \[\s*itemDashboard,\s*itemOrdenes,)',
           r'\1\n                          itemTareas,', c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Arrays updated again")
