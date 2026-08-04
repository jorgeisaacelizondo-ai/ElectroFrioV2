
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('shiftSubtext.textContent = Entrada registrada a las ;', 'shiftSubtext.textContent = \Entrada registrada a las \;')
c = c.replace('shiftSubtext.textContent = Entrada registrada a las ;', 'shiftSubtext.textContent = \Entrada registrada a las \;')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done string fix 3')

