const fs=require('fs');
const html=fs.readFileSync('ESP/index.html','utf8');
const a=html.indexOf('function segs()');
const b=html.indexOf('function pts(',a);
if(a<0||b<0)throw new Error('Cannot locate shipped Spanish word engine');
const engine=html.slice(a,b);
const C=10,R=20;
let board,W,BL;
eval(engine);

function index(){BL=new Map();for(const w of W){if(!BL.has(w.length))BL.set(w.length,[]);BL.get(w.length).push(w)}}
function blank(){board=Array.from({length:R},()=>Array(C).fill(null))}
function putH(y,x,s){[...s].forEach((l,i)=>board[y][x+i]={l})}
function putV(y,x,s){[...s].forEach((l,i)=>board[y+i][x]={l})}
function setup(words){W=new Set(words);index();blank()}
function names(){return find().map(x=>x.w).sort()}
function eq(actual,expected,label){const A=JSON.stringify(actual),E=JSON.stringify(expected);if(A!==E)throw new Error(`${label}: ${A} != ${E}`)}
function ok(v,label){if(!v)throw new Error(label)}

setup(['casa']);putH(19,3,'casa');eq(names(),['casa'],'horizontal CASA');
setup(['mar']);putV(17,4,'mar');eq(names(),['mar'],'vertical MAR');
setup(['sol','ola']);putH(19,2,'sola');eq(names(),['ola','sol'],'equal-length overlap SOL+OLA');
setup(['mar','rey']);putH(10,3,'mar');putV(10,5,'rey');eq(names(),['mar','rey'],'horizontal/vertical crossing');
setup(['pan','panda']);putH(19,2,'panda');eq(names(),['panda'],'longest overlapping word wins');
setup(['sol','mar']);putH(19,0,'sol');putH(19,5,'mar');eq(names(),['mar','sol'],'independent words both clear');
setup(['casa','cosa','asa']);putH(19,2,'c★sa');let f=find();ok(f.some(x=>x.w.length===4),'wildcard chooses maximum length');ok(!f.some(x=>x.w.length===3),'short wildcard word suppressed');
setup([]);putH(19,2,'zzz');eq(names(),[],'garbage absent from dictionary does not clear');

console.log('WORDtris Spanish shipped matching logic: all tests passed');
