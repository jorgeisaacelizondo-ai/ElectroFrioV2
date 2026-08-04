import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

helper = '''        function getSyncedDate() {
            return new Date(Date.now() + timeOffset);
        }

        // Helper para obtener fecha local en formato YYYY-MM-DD
        function getLocalISODate(dateObj) {
            const yyyy = dateObj.getFullYear();
            const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
            const dd = String(dateObj.getDate()).padStart(2, '0');
            return `${yyyy}-${mm}-${dd}`;
        }'''

c = re.sub(r'\s*function getSyncedDate\(\) \{\s*return new Date\(Date\.now\(\) \+ timeOffset\);\s*\}', '\n' + helper + '\n', c)

c = re.sub(r'getSyncedDate\(\)\.toISOString\(\)\.split\(\'T\'\)\[0\]', 'getLocalISODate(getSyncedDate())', c)
c = re.sub(r'now\.toISOString\(\)\.split\(\'T\'\)\[0\]', 'getLocalISODate(now)', c)
c = re.sub(r'today\.toISOString\(\)\.split\(\'T\'\)\[0\]', 'getLocalISODate(today)', c)
c = re.sub(r'start\.toISOString\(\)\.split\(\'T\'\)\[0\]', 'getLocalISODate(start)', c)
c = re.sub(r'end\.toISOString\(\)\.split\(\'T\'\)\[0\]', 'getLocalISODate(end)', c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done!')
