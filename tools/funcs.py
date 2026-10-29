import os,re,sys,collections
base=sys.argv[1]
fz={'jianba_2','shishio','sidai','soifong','zhitian'}
per={}
for n in sorted(os.listdir(base)):
    if n=='game':continue
    s=set()
    for r,_,fs in os.walk(os.path.join(base,n)):
        for f in fs:
            if f.endswith('.as'):
                t=open(os.path.join(r,f),encoding='utf-8',errors='replace').read()
                s|=set(re.findall(r'^\s*function (\w+)\(',t,re.M))
    per[n]=s
fighters=[n for n in per if n not in fz]
c=collections.Counter(f for n in fighters for f in per[n])
common=sorted(f for f,k in c.items() if k==len(fighters))
print(len(fighters),'fighters; functions in ALL:',len(common))
print(' '.join(common))
print('\nin >=80%:',' '.join(sorted(f for f,k in c.items() if len(fighters)*0.8<=k<len(fighters))))
for n in fighters: print(f'{n:10} funcs={len(per[n]):4} missing_common80={[f for f,k in c.items() if k>=len(fighters)*0.8 and f not in per[n]][:8]}')
print('\nfz funcs:'); 
for n in sorted(fz): print(n,sorted(per[n]))
