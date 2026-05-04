Aplica un segundo patch mínimo para eliminar el bloque 
Symbol EURUSD_M1_dukas residual. Hazlo con regex quirúrgico,
sin tocar nada más.

import zipfile, re

with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx') as z:
    task_xml = z.read('Build-Task1.xml').decode()
    config_xml = z.read('config.xml').decode()

# Eliminar bloque <Symbol name="EURUSD_M1_dukas"...>...</Symbol>
antes = task_xml.count('EURUSD')
task_xml_patched = re.sub(
    r'\s*<Symbol name="EURUSD_M1_dukas"[^>]*>.*?</Symbol>',
    '',
    task_xml,
    flags=re.DOTALL
)
despues = task_xml_patched.count('EURUSD')
print(f"EURUSD antes: {antes}, después: {despues}")
print(f"Líneas eliminadas: {task_xml.count(chr(10)) - task_xml_patched.count(chr(10))}")

# Solo escribir si quedó 0 EURUSD
if despues == 0:
    with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx', 
                         'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('config.xml', config_xml)
        zf.writestr('Build-Task1.xml', task_xml_patched)
    print("CFX actualizado - 0 referencias EURUSD")
else:
    print(f"[ERROR] Quedan {despues} referencias EURUSD - revisar")

# Verificación final
with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx') as z:
    t = z.read('Build-Task1.xml').decode()
    print(f"EURUSD: {t.count('EURUSD')}")
    print(f"XAUUSD: {t.count('XAUUSD')}")
    print(f"undefined: {'undefined' in t}")