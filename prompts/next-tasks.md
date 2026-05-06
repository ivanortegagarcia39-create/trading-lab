Modifica el CFX del Builder para relajar los filtros de aceptación:

import zipfile, re, shutil

shutil.copy2(r'D:/user/projects/Builder/project.cfx',
             r'D:/user/projects/Builder/project.cfx.bak_filters')

with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx') as z:
    task = z.read('Build-Task1.xml').decode()
    config = z.read('config.xml').decode()

# Cambiar PF mínimo de 1.3 a 1.1
task = task.replace(
    '<Condition>ProfitFactor > 1.3</Condition>',
    '<Condition>ProfitFactor > 1.1</Condition>'
)

# Cambiar ReturnDDRatio de 4 a 2
task = task.replace(
    '<Condition>ReturnDDRatio > 4</Condition>',
    '<Condition>ReturnDDRatio > 2</Condition>'
)

with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx',
                     'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('config.xml', config)
    z.writestr('Build-Task1.xml', task)

print("Filtros relajados")

# Verificar
with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx') as z:
    t = z.read('Build-Task1.xml').decode()
    conditions = re.findall(r'<Condition>[^<]+</Condition>', t)
    for c in conditions:
        print(c)