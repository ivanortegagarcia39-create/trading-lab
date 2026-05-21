PYTHONUTF8=1 python -c "
import zipfile, glob, re, os, base64, struct

def parse_sqstats(data):
    s = {}
    trades_set = False
    i = 0
    while i < len(data) - 5:
        t = data[i]
        if t == 0x03:
            fid = data[i+1]
            val = struct.unpack('>f', data[i+2:i+6])[0]
            if ('F', fid) not in s:
                s[('F', fid)] = val
            i += 6
        elif t == 0x01:
            fid = data[i+1]
            val = struct.unpack('>I', data[i+2:i+6])[0]
            if fid == 0x01 and not trades_set:
                s['trades'] = val
                trades_set = True
            i += 6
        else:
            i += 1
    return s

files = sorted(glob.glob(r'D:\user\projects\Builder\databanks\Results\*.sqx'))
print(f'Total: {len(files)}')
print(f'{\"Nombre\":<22} {\"PF\":>5} {\"DD%\":>5} {\"Trades\":>7}')
print('-' * 42)

for f in files:
    try:
        with zipfile.ZipFile(f) as z:
            rx = next(n for n in z.namelist() if n.endswith('Results.xml'))
            xml = z.read(rx).decode(errors='ignore')
        m = re.search(r'<RobustnessOriginalResults>.*?<SQStats[^>]*>(.*?)</SQStats>', xml, re.DOTALL)
        if not m: continue
        data = base64.b64decode(m.group(1).strip())
        s = parse_sqstats(data)
        pf = round(s.get(('F', 0x2E), 0.0), 2)
        dd = round(s.get(('F', 0x5B), 0.0), 2)
        trades = s.get('trades', 0)
        nombre = os.path.basename(f).replace('.sqx','')[-20:]
        print(f'{nombre:<22} {pf:>5.2f} {dd:>5.2f} {trades:>7}')
    except: pass
"