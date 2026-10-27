const fs=require('fs');
function applyUiFlags(main,flags){
 const enabled=(key)=>flags[key]===true;
 const routeModules={'/dashboard':'resumen','/net-worth':'resumen','/insights':'analisis','/holdings':'tenencias','/import':'importacion','/activities':'movimientos','/goals':'objetivos','/assistant':'asistente','/connect':'connect','/accounts':'cuentas','/settings/accounts':'cuentas','/settings/portfolios':'carteras','/settings/general':'preferencias','/settings/appearance':'preferencias','/settings/exports':'respaldos','/settings/agent-access':'agentes','/settings/about':'creditos','/settings/connect':'connect','/settings/securities':'instrumentos','/settings/taxonomies':'clasificaciones','/settings/market-data':'mercado','/settings/ai-providers':'asistente','/settings/addons':'extensiones','/settings/contribution-limits':'limites','/settings/spending':'gastos'};
 function allowed(href){
  const p=String(href||'').split('?')[0];
  if(p==='#update-portfolio')return flags.mercado===true;
  if(p==='#recalculate-portfolio')return flags.movimientos===true;
  if(p.startsWith('#'))return true;
  if(href==='/activities/add?tab=holdings')return flags.importacion===true;
  const key=Object.keys(routeModules).sort((a,b)=>b.length-a.length).find(k=>p===k||p.startsWith(k+'/'));
  return key?flags[routeModules[key]]===true:true;
 }
 const prefix='const MINOS_UI_FLAGS='+JSON.stringify(flags)+';const MINOS_UI_ROUTES='+JSON.stringify(routeModules)+';const minosUiAllowed='+allowed.toString().replaceAll('flags.','MINOS_UI_FLAGS.').replaceAll('flags[','MINOS_UI_FLAGS[').replaceAll('routeModules','MINOS_UI_ROUTES')+';';
 function replaceOnce(a,b){if(!main.includes(a))throw Error('UI anchor missing: '+a.slice(0,90));main=main.replace(a,b);}
 const start=main.indexOf('function N4n(e){'),end=main.indexOf('function EWe()',start);
 if(start<0||end<0)throw Error('Navigation function missing');
 const old=main.slice(start,end);
 let nav=old.replace('function N4n(e){return{','function N4n(e){const nav={');
 if(!nav.endsWith('}}'))throw Error('Unexpected navigation ending');
 nav=nav.slice(0,-2)+'};if(MINOS_UI_FLAGS.cuentas)nav.primary.unshift({icon:s.jsx(D.CreditCard,{className:"size-6"}),title:e("settings:nav.items.accounts"),href:"/settings/accounts",keywords:["cuentas","accounts"]});if(MINOS_UI_FLAGS.carteras)nav.primary.push({icon:s.jsx(D.Folder,{className:"size-6"}),title:e("settings:nav.items.portfolios"),href:"/settings/portfolios"});nav.primary=nav.primary.filter(x=>minosUiAllowed(x.href));return nav}';
 main=main.slice(0,start)+nav+main.slice(end);
 replaceOnce('u=d.useMemo(()=>n??[],[n]);','u=d.useMemo(()=>MINOS_UI_FLAGS.extensiones?n??[]:[],[n]);');
 replaceOnce('return[...Q,...ie]},[p,_,A,j,v,r.pathname,c,C,e])','return[...Q,...ie].filter(item=>minosUiAllowed(item.href))},[p,_,A,j,v,r.pathname,c,C,e])');
 replaceOnce(']}],[e,!0]),i=t.pathname===',' ]}].map(section=>({...section,items:section.items.filter(item=>minosUiAllowed("/settings/"+item.href))})).filter(section=>section.items.length>0),[e,!0]),i=t.pathname===');
 replaceOnce('}],U=[...z,...L],B=U.length>0','}].filter(item=>minosUiAllowed(item.href)),U=[...z,...L],B=U.length>0');
 return {main:prefix+main,allowed};
}
module.exports={applyUiFlags};
