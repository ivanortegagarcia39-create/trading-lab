PYTHONUTF8=1 python -c "
import zipfile, io, shutil

cfx = r'D:/user/projects/Builder/project.cfx'
shutil.copy2(cfx, cfx + '.bak_sl_fix')

with zipfile.ZipFile(cfx) as z:
    task = z.read('Build-Task1.xml').decode()
    config = z.read('config.xml').decode()

# Cambiar SL 30-80 -> 20-60
task = task.replace(
    '<Param key=\"MinimumSL\" className=\"MinMaxSLPT\">30</Param>',
    '<Param key=\"MinimumSL\" className=\"MinMaxSLPT\">20</Param>'
)
task = task.replace(
    '<Param key=\"MaximumSL\" className=\"MinMaxSLPT\">80</Param>',
    '<Param key=\"MaximumSL\" className=\"MinMaxSLPT\">60</Param>'
)

# Cambiar PT 60-200 -> 40-120
task = task.replace(
    '<Param key=\"MinimumPT\" className=\"MinMaxSLPT\">60</Param>',
    '<Param key=\"MinimumPT\" className=\"MinMaxSLPT\">40</Param>'
)
task = task.replace(
    '<Param key=\"MaximumPT\" className=\"MinMaxSLPT\">200</Param>',
    '<Param key=\"MaximumPT\" className=\"MinMaxSLPT\">120</Param>'
)

buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
    zout.writestr('config.xml', config)
    zout.writestr('Build-Task1.xml', task)

with open(cfx, 'wb') as f:
    f.write(buf.getvalue())

print('SL/PT actualizados: SL 20-60, PT 40-120')
"