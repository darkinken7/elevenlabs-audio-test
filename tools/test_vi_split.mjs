import { deParts } from '../source/vi_split.mjs';
const bad=['sau Verb: Morgen fahre ich …','Platzhalter cho dass-Satz','Konjunktiv II trong als-dass-Satz','Überraschung — súp nóng quá!','kurz/schnell — xem mail chút','phía sau','Pos.2, ngay sau desto + Komparativ'];
const good=['Das ist das beste Café der Stadt.','Sie trinkt jeden Morgen aus Gewohnheit im Café einen Kaffee.','Ich gehe heute wegen der Kälte nach Hause.'];
let f=0;for(const t of bad){const c=deParts(t).cls;if(c==='de'){f++;console.log('FAIL bad->de:',t)}}
for(const t of good){const c=deParts(t).cls;if(c!=='de'){f++;console.log('FAIL good->',c,t)}}
console.log(f?`${f} fail`:'ALL PASS');
