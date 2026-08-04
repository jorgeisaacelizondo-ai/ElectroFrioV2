
import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(r'(<button[^>]*data-module="mapa"[^>]*)>', r'\1 style="display:none !important;">', c)
c = c.replace('window.startLocationTracking = function(role) {', 'window.startLocationTracking = function(role) { return; // MAP DESHABILITADO\n')
c = c.replace('window.initTechMap = function() {', 'window.initTechMap = function() { return; // MAP DESHABILITADO\n')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')

