import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix the visibleAndOrdered arrays for admin, premium, and collab

admin_array_orig = r'''                  if \(role === 'Administrador'\) \{\s*visibleAndOrdered = \[\s*itemDashboard,\s*itemOrdenes,\s*itemCalendario,'''
admin_array_new = r'''                  if (role === 'Administrador') {
                      visibleAndOrdered = [
                          itemDashboard,
                          itemOrdenes,
                          itemTareas,
                          itemCalendario,'''
c = re.sub(admin_array_orig, admin_array_new, c)

premium_array_orig = r'''                  \} else if \(isPremium\) \{\s*visibleAndOrdered = \[\s*itemDashboard,\s*itemOrdenes,\s*itemDatabase,'''
premium_array_new = r'''                  } else if (isPremium) {
                      visibleAndOrdered = [
                          itemDashboard,
                          itemOrdenes,
                          itemTareas,
                          itemDatabase,'''
c = re.sub(premium_array_orig, premium_array_new, c)

collab_array_orig = r'''                  \} else \{\s*visibleAndOrdered = \[\s*itemDashboard,\s*itemOrdenes,\s*itemDatabase,'''
collab_array_new = r'''                  } else {
                      visibleAndOrdered = [
                          itemDashboard,
                          itemOrdenes,
                          itemTareas,
                          itemDatabase,'''
c = re.sub(collab_array_orig, collab_array_new, c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Arrays updated")
