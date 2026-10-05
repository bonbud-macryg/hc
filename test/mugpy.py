import sys
M=0xffffffff
def rotl(x,r): return ((x<<r)|(x>>(32-r)))&M
def muk(seed,length,key):
    c1,c2=0xcc9e2d51,0x1b873593
    h=seed&M
    kb=key.to_bytes(max(length,(key.bit_length()+7)//8,1),'little')
    nb=length//4
    for i in range(nb):
        k=int.from_bytes(kb[i*4:i*4+4],'little')
        k=(k*c1)&M; k=rotl(k,15); k=(k*c2)&M
        h^=k; h=rotl(h,13); h=(h*5+0xe6546b64)&M
    t=length&3; k=0; tail=nb*4
    if t:
        for j in range(t-1,-1,-1):
            k^=(kb[tail+j] if tail+j<len(kb) else 0)<<(8*j)
        k=(k*c1)&M; k=rotl(k,15); k=(k*c2)&M; h^=k
    h^=length&M
    h^=h>>16; h=(h*0x85ebca6b)&M; h^=h>>13; h=(h*0xc2b2ae35)&M; h^=h>>16
    return h
def mum(syd,fal,key):
    wyd=(key.bit_length()+7)//8
    for i in range(8):
        haz=muk(syd,wyd,key)
        ham=(haz>>31)^(haz&0x7fffffff)
        if ham: return ham
        syd+=1
    return fal
def mugtext(s):
    # iterative over canonical "[h t]" with hex atoms
    stack=[]; i=0; n=len(s); vals=[]
    ops=[]
    # tokenize
    import re
    toks=re.findall(r'\[|\]|[0-9a-f]+',s)
    st=[]
    for t in toks:
        if t=='[': st.append('[')
        elif t==']':
            tl=st.pop(); hd=st.pop(); st.pop()
            st.append(mum(0xdeadbeef,0xfffe,hd|(tl<<32)))
        else:
            st.append(mum(0xcafebabe,0x7fff,int(t,16)))
    return st[0]
if __name__=='__main__':
    print(mugtext(sys.stdin.read()))
