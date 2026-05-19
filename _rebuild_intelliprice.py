base = "/home/acuba/Proyectos/intelliprice"
with open(f"{base}/app/page.tsx") as f:
    c = f.read()
old = '</section><section className="relative border-t border-white/5 py-16 px-6 overflow-hidden">'
badges = '<div className="flex gap-6 mt-10 items-center justify-center"><a href="https://github.com/Treevu-ai/cli-market-world" target="_blank"><img src="https://img.shields.io/github/stars/Treevu-ai/cli-market-world?style=social" alt="GitHub stars" style={{height:20}}/></a><a href="https://pypi.org/project/cli-market/" target="_blank"><img src="https://img.shields.io/pypi/dm/cli-market?style=social" alt="PyPI downloads" style={{height:20}}/></a></div></section><section className="relative border-t border-white/5 py-16 px-6 overflow-hidden">'
c = c.replace(old, badges, 1)
with open(f"{base}/app/page.tsx", "w") as f:
    f.write(c)
print("OK")
