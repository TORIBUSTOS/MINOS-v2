const fs=require('fs');
const path=require('path');
function buildTheme(root,target,main){
 const config=JSON.parse(fs.readFileSync(path.join(root,'assets/tokens.json'),'utf8'));
 const ui=JSON.parse(fs.readFileSync(path.join(root,'themes.json'),'utf8'));
 if(!ui.themes.light.enabled||!ui.themes.dark.enabled)throw Error('Native light and dark themes must remain available');
 const safe=s=>{if(typeof s!=='string'||/[;{}<>]/.test(s))throw Error('Unsafe CSS token');return s};
 let css='/* Generated from assets/tokens.json + themes.json. Do not edit output. */\n';
 const common={...ui.tokens,'font-family-ui':config.font.body,'font-family-display':config.font.display,'font-family-mono':config.font.mono};
 const block=(selector,tokens)=>selector+'{'+Object.entries(tokens).map(([k,v])=>'--'+k+':'+safe(v)+';').join('')+'}\n';
 css+=block(':root',common);
 for(const [id,theme] of Object.entries(ui.themes)){
  if(!theme.enabled)continue;
  const colors=Object.fromEntries(Object.entries(theme.tokens).map(([k,v])=>[k,v.startsWith('$')?config.color[v.slice(1)]:v]));
  css+=block(id==='light'?':root,html.light':'html.dark',colors);
 }
 const skins=require('./skins.cjs').buildSkins(ui,block);css+=skins.css;
 const aliases={background:'bg-base',foreground:'text-main',card:'bg-surface','card-foreground':'text-main',popover:'bg-surface-raised','popover-foreground':'text-main',primary:'primary-action','primary-foreground':'text-on-action',secondary:'bg-section','secondary-foreground':'text-main',muted:'bg-section','muted-foreground':'text-muted',accent:'bg-hover','accent-foreground':'text-main',destructive:'danger','destructive-foreground':'text-on-danger',success:'state-success',warning:'state-warning',info:'state-info',border:'border-subtle',input:'border-strong','input-bg':'bg-surface',ring:'focus-ring',sidebar:'bg-section','sidebar-foreground':'text-main','sidebar-primary':'primary-action','sidebar-primary-foreground':'text-on-action','sidebar-accent':'bg-hover','sidebar-accent-foreground':'text-main','sidebar-border':'border-subtle','sidebar-ring':'focus-ring','button-radius':'radius-sm','control-radius':'radius-sm','card-radius':'radius-md','popup-radius':'radius-md','dialog-radius':'radius-md','card-shadow':'shadow-raised'};
 css+=':root,html.light,html.dark{'+Object.entries(aliases).map(([k,v])=>'--'+k+':var(--'+v+');').join('')+'}\n';
 css+=fs.readFileSync(path.join(root,'app.css'),'utf8');
 fs.writeFileSync(path.join(target,'minos-theme-v8.css'),css);
 const asset=path.resolve(root,config.asset.symbol);if(!asset.startsWith(path.resolve(root,'assets')+path.sep))throw Error('Symbol must be under branding/assets');
 fs.copyFileSync(asset,path.join(target,'minos-symbol-v5.svg'));
 function once(a,b){if(main.split(a).length!==2)throw Error('Theme anchor changed: '+a.slice(0,70));main=main.replace(a,b)}
 once('children:"Wealthfolio"})]}),s.jsxs(ae,{type:"button",variant:"ghost",onClick:()=>{const l=new KeyboardEvent', 'children:'+JSON.stringify(config.brand.name+' '+config.brand.descriptor)+'})]}),s.jsxs(ae,{type:"button",variant:"ghost",onClick:()=>{const l=new KeyboardEvent');
 main=main.replaceAll('src:"/logo.png"','src:"/minos-symbol-v5.svg"').replaceAll('src:"/logo-gold.png",alt:"Wealthfolio"','src:"/minos-symbol-v5.svg",alt:'+JSON.stringify(config.brand.name+' '+config.brand.descriptor));
 once('text-md text-foreground/90 ms-2 font-serif text-xl font-bold','minos-brand-name text-md text-foreground/90 ms-2 font-serif text-xl font-bold');
 const rowStart=main.indexOf('function uet('),rowEnd=main.indexOf('uet.Skeleton=',rowStart);
 if(rowStart<0||rowEnd<0)throw Error('Account row changed');
 let row=main.slice(rowStart,rowEnd);
 const rowEdits=[
 ['className:"flex items-center justify-between p-4"','className:"minos-account-row flex items-center justify-between p-4"'],
 ['className:"flex items-center gap-3"','className:"minos-account-main flex min-w-0 flex-1 items-center gap-3"'],
 ['className:"grid gap-1"','className:"minos-account-copy min-w-0 grid gap-1"'],
 ['className:"text-muted-foreground flex items-center gap-1.5 text-sm"','className:"minos-account-details text-muted-foreground flex flex-wrap items-center gap-1.5 text-sm"']
 ];
 for(const [a,b] of rowEdits){if(!row.includes(a))throw Error('Account row anchor changed');row=row.replace(a,b)}
 main=main.slice(0,rowStart)+row+main.slice(rowEnd);
 for(const key of ['section_active','section_hidden_archived']){
 const a='s.jsx("h3",{className:"text-muted-foreground text-sm font-medium",children:e("settings:accounts.'+key+'")})';
 once(a,a.replace('s.jsx("h3"','s.jsx("h2"'));
 }
 const intro="s.jsxs(\"section\",{className:\"minos-account-context\",\"aria-label\":\"Resumen de cuentas\",children:[s.jsxs(\"p\",{children:[s.jsx(\"strong\",{children:t.length+(t.length===1?\" cuenta\":\" cuentas\")}),s.jsx(\"span\",{children:[...new Set(t.map(account=>account.currency))].join(\" · \")})]}),s.jsx(fn,{to:\"/settings/appearance\",className:\"minos-theme-link\",children:\"Personalizar apariencia\"})]})";
 once('"data-testid":"settings-accounts-page",className:"space-y-6",children:[s.jsx(Wi,','"data-testid":"settings-accounts-page",className:"minos-accounts space-y-6",children:[s.jsx(Wi,');
 const header="e(\"settings:accounts_add_button\")]})]})}),s.jsx(ts,{})";
 once(header,header.replace('s.jsx(ts,{})',intro+',s.jsx(ts,{})'));
 once("s.jsx(\"h2\",{className:\"text-2xl font-bold tracking-tight\",children:e(\"settings:title\")})",'s.jsxs("div",{className:"minos-settings-identity",children:[s.jsx("img",{src:"/minos-symbol-v5.svg",alt:"",width:40,height:40}),s.jsxs("div",{children:[s.jsx("p",{children:'+JSON.stringify(config.brand.name+" "+config.brand.descriptor)+'}),s.jsx("p",{className:"minos-settings-label",children:e("settings:title")})]})]})');
 const identity='s.jsxs("div",{className:"minos-settings-identity",children:[s.jsx("img",{src:"/minos-symbol-v5.svg",alt:"",width:40,height:40}),s.jsxs("div",{children:[s.jsx("p",{children:'+JSON.stringify(config.brand.name+" "+config.brand.descriptor)+'}),s.jsx("p",{className:"minos-settings-label",children:e("settings:title")})]})]})';
 once(identity,'s.jsxs("div",{className:"minos-settings-toolbar",children:['+identity+',s.jsx(MinosSkinPicker,{})]})');
 const appearanceLink='s.jsx(fn,{to:"/settings/appearance",className:"minos-theme-link",children:"Personalizar apariencia"})';
 once(appearanceLink,'s.jsxs("div",{className:"minos-skin-actions",children:[s.jsx(MinosSkinPicker,{}),'+appearanceLink+']})');
 once('s.jsx(BOn,{})','s.jsxs(s.Fragment,{children:[s.jsx("div",{className:"minos-appearance-skin",children:s.jsx(MinosSkinPicker,{})}),s.jsx(BOn,{})]})');
 return skins.prefix+main;
}
module.exports={buildTheme};
