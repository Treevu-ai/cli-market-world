import os, sys, asyncio
sys.path.insert(0, '/home/acuba/Proyectos/cli-market-world')
os.chdir('/home/acuba/Proyectos/cli-market-world')
os.environ['DATABASE_URL'] = 'postgres://none:none@localhost/none'
os.environ['PYTHONUNBUFFERED'] = '1'
sys.argv = ['collect_prices.py', '--daemon']
import collect_prices
asyncio.run(collect_prices.main())
