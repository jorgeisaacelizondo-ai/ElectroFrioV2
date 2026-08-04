import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix allowedModules for premium
c = re.sub(r'(allowedModules = \[\'dashboard\', \'ordenes\', )(\'database\', \'fichajes\', \'presupuesto\'\];)',
           r"\1'tareas', \2", c)

# Fix allowedModules for collab
c = re.sub(r'(allowedModules = \[\'dashboard\', \'ordenes\', )(\'database\', \'fichajes\'\];)',
           r"\1'tareas', \2", c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Allowed modules updated")
