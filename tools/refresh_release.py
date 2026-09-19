from pathlib import Path
import zipfile,re
root=Path(__file__).resolve().parents[1]
p=root/'tools/build_reference.py'
s=p.read_text(encoding='utf-8').replace('宗教：教会 |','宗教：圣像崇敬 |').replace('宗教：公民 |','宗教：圣像破坏 |').replace('最终人口+35%、稳定+20、战争支持+20、科研−10%。','最终人口+35%、稳定+20、战争支持+15、科研−8%、陆军组织度恢复+5%。').replace('最终人口+25%、稳定+15、战争支持+10、科研+10%。','最终人口+25%、稳定+15、战争支持+10、科研+8%、每日政治点+0.10、法律成本−5%。').replace('另教育决议60天','另整顿教产与学校决议60天')
p.write_text(s,encoding='utf-8')
import runpy
runpy.run_path(str(p))
with zipfile.ZipFile(root/'dist/RomaInvicta-0.2.0.zip','w',zipfile.ZIP_DEFLATED) as z:
 for folder in ['common','events','gfx','interface','localisation']:
  for p in sorted((root/folder).rglob('*')):
   if p.is_file():z.write(p,'roma_restoration/'+p.relative_to(root).as_posix())
 for name in ['descriptor.mod','README.md','docs/当前完整国策与效果.md','docs/validation_report.json']:z.write(root/name,'roma_restoration/'+name)
 z.writestr('roma_restoration.mod',re.sub(r'path="[^"]*"','path="mod/roma_restoration"',(root/'roma_restoration.mod').read_text()))
with zipfile.ZipFile(root/'dist/RomaInvicta-0.2.0.zip') as z:assert z.testzip() is None