const KEY='minos-visual-theme';
function buildSkins(ui,block){
 const entries=Object.entries(ui.skins||{}).filter(([,v])=>v.enabled);
 if(!entries.length||!entries.some(([id])=>id===ui.defaultSkin))throw Error('Invalid default visual theme');
 const options=entries.map(([id,v])=>{if(!/^[a-z0-9-]+$/.test(id))throw Error('Invalid visual theme id');return{id,label:v.label}});
 let css='';
 for(const [id,skin] of entries){
  css+=block('html[data-minos-theme="'+id+'"]',skin.tokens||{});
  for(const [mode,tokens] of Object.entries(skin.modes||{}))css+=block(mode==='light'?'html[data-minos-theme="'+id+'"]':'html.dark[data-minos-theme="'+id+'"]',tokens);
 }
 const prefix='const MINOS_SKIN_OPTIONS='+JSON.stringify(options)+';const MINOS_DEFAULT_SKIN='+JSON.stringify(ui.defaultSkin)+';const MINOS_SKIN_KEY='+JSON.stringify(KEY)+';'+
 'function MinosSkinPicker(){const [value,setValue]=d.useState(()=>{const id=document.documentElement.dataset.minosTheme;return MINOS_SKIN_OPTIONS.some(x=>x.id===id)?id:MINOS_DEFAULT_SKIN});d.useEffect(()=>{const sync=()=>setValue(document.documentElement.dataset.minosTheme||MINOS_DEFAULT_SKIN);const storage=event=>{if(event.key===MINOS_SKIN_KEY){const id=MINOS_SKIN_OPTIONS.some(x=>x.id===event.newValue)?event.newValue:MINOS_DEFAULT_SKIN;document.documentElement.dataset.minosTheme=id;sync()}};window.addEventListener("minos:theme-change",sync);window.addEventListener("storage",storage);return()=>{window.removeEventListener("minos:theme-change",sync);window.removeEventListener("storage",storage)}},[]);return s.jsxs("label",{className:"minos-skin-picker",children:[s.jsx("span",{children:"Estilo visual"}),s.jsx("select",{"aria-label":"Estilo visual de Minos Capital",value,onChange:event=>{const id=event.target.value;if(!MINOS_SKIN_OPTIONS.some(x=>x.id===id))return;document.documentElement.dataset.minosTheme=id;setValue(id);try{localStorage.setItem(MINOS_SKIN_KEY,id)}catch{}window.dispatchEvent(new Event("minos:theme-change"))},children:MINOS_SKIN_OPTIONS.map(option=>s.jsx("option",{value:option.id,children:option.label},option.id))})]})}';
 const bootstrap='(()=>{const options='+JSON.stringify(options.map(x=>x.id))+';let value='+JSON.stringify(ui.defaultSkin)+';try{const saved=localStorage.getItem('+JSON.stringify(KEY)+');if(options.includes(saved))value=saved}catch{}document.documentElement.dataset.minosTheme=value})();';
 return {css,prefix,bootstrap};
}
module.exports={buildSkins};
