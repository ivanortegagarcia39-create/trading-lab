Restaura desde el backup original y aplica SOLO el patch 
EURUSD->XAUUSD. Sin reempaquetar ni normalizar nada más.

import zipfile, glob, shutil

backups = sorted(glob.glob(r'D:/user/projects/Builder/project.cfx.bak_*'))
original_cfx = backups[0]

# Leer Build-Task1.xml del backup original (sin normalizar)
with zipfile.ZipFile(original_cfx) as z:
    task_xml = z.read('Build-Task1.xml').decode()
    config_xml = z.read('config.xml').decode()

# Aplicar SOLO el patch EURUSD->XAUUSD
task_xml_patched = task_xml.replace(
    'symbol="EURUSD_M1_dukas"',
    'symbol="XAUUSD_M1_dukas"'
)

# Verificar que solo cambió 1 línea
changes = sum(1 for a, b in zip(
    task_xml.split('\n'), 
    task_xml_patched.split('\n')
) if a != b)
print(f"Líneas modificadas: {changes} (esperado: 1)")

# Backup del CFX actual antes de sobreescribir
shutil.copy2(
    r'D:/user/projects/Builder/project.cfx',
    r'D:/user/projects/Builder/project.cfx.bak_pre_restore'
)

# Reempaquetar con los bytes originales + patch mínimo
with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx', 'w', 
                     zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('config.xml', config_xml)
    zf.writestr('Build-Task1.xml', task_xml_patched)

print("CFX restaurado con patch mínimo")

# Verificar
with zipfile.ZipFile(r'D:/user/projects/Builder/project.cfx') as z:
    t = z.read('Build-Task1.xml').decode()
    print(f"EURUSD restante: {t.count('EURUSD_M1_dukas')}")
    print(f"XAUUSD presente: {t.count('XAUUSD_M1_dukas')}")
    print(f"undefined presente: {'undefined' in t}")

Cuando termines:
git add -A && git commit -m "fix: restaurar CFX desde backup original con patch minimo EURUSD->XAUUSD" && git push origin main