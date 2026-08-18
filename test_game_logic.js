const fs=require('fs');
const html=fs.readFileSync('index.html','utf8');
const a=html.indexOf('function segs()');
const b=html.indexOf('function pts(',a);
if(a<0||b<0)throw new Error('Cannot locate shipped word engine');
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

setup(['том']);putH(19,3,'том');eq(names(),['том'],'horizontal ТОМ');
setup(['дуб']);putV(17,4,'дуб');eq(names(),['дуб'],'vertical ДУБ');
setup(['еду','дуб']);putH(19,2,'едуб');eq(names(),['дуб','еду'],'equal-length overlap ЕДУ+ДУБ');
setup(['кот','том']);putH(10,3,'кот');putV(10,5,'том');eq(names(),['кот','том'],'horizontal/vertical crossing');
setup(['кот','том','котом']);putH(19,2,'котом');eq(names(),['котом'],'longest overlapping word wins');
setup(['кот','дуб']);putH(19,0,'кот');putH(19,5,'дуб');eq(names(),['дуб','кот'],'independent words both clear');
setup(['кот','коты','роты']);putH(19,2,'★оты');let f=find();ok(f.some(x=>x.w.length===4),'wildcard chooses maximum length');ok(!f.some(x=>x.w.length===3),'short wildcard word suppressed');
setup(['ски']);putH(19,2,'ски');eq(names(),['ски'],'engine recognizes only words explicitly supplied');
setup([]);putH(19,2,'ски');eq(names(),[],'garbage absent from dictionary does not clear');

console.log('WORDtris shipped matching logic: all tests passed');
