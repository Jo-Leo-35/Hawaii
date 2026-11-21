const $ = (selector) => document.querySelector(selector);
const statusLabels = {planned:'行程安排',pending:'待確認',confirmed:'已安排',optional:'候選備案'};
let trip;
let currentDay = 0;
let ownerFilter = 'all';
let placeCategory = 'all';
let showAllPlaces = false;
const categories = [
  {name:'美食',value:'餐飲',icon:'fork-knife',color:'#ff6200'},
  {name:'購物',value:'購物',icon:'shopping-bag',color:'#7951e8'},
  {name:'住宿',value:'住宿',icon:'bed',color:'#edb000'},
  {name:'交通',value:'交通',icon:'bus',color:'#0999e9'},
  {name:'自然',value:'自然',icon:'mountains',color:'#1a9e59'},
  {name:'活動',value:'活動',icon:'person-simple-run',color:'#ef5a77'},
];

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function badge(status) { return element('span', `status status-${status}`, statusLabels[status] || statusLabels.planned); }
function icon(name) {
  const image = element('img','icon');
  image.src = `./assets/icons/${name}.svg`;image.alt='';return image;
}
function placePhoto(place, className) {
  if (!place?.image) return null;
  const image=element('img',className);image.src=place.image;image.alt=place.imageAlt;
  image.loading='lazy';image.width=640;image.height=400;return image;
}
function publicLink(label, href, className='official-link') {
  const url = new URL(href);
  if (url.protocol !== 'https:') throw new Error('Only HTTPS resources are allowed');
  const a = element('a', className, label);
  a.href = url.href;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.setAttribute('aria-label', `${label}（另開分頁）`);
  return a;
}
function placeById(id) { return trip.places.find(place => place.id === id); }
function mapLink(place) {
  const url = new URL(place.mapUrl);
  if (url.hostname !== 'www.google.com' || !url.pathname.startsWith('/maps/place/')) {
    throw new Error('Use a verified Google Maps place listing');
  }
  const link = publicLink('Google Maps', url.href, 'map-link');
  link.setAttribute('aria-label', `${place.name}：Google Maps（另開分頁）`);
  return link;
}
function renderDay(index, focus=false) {
  currentDay = index;
  const day = trip.days[index];
  document.querySelectorAll('.day-tab').forEach((tab, i) => {
    tab.setAttribute('aria-selected', String(index === i));
    tab.tabIndex = index === i ? 0 : -1;
  });
  const panel = $('#day-panel');
  panel.replaceChildren();
  panel.setAttribute('aria-labelledby', `tab-${day.id}`);
  const banner = element('div', 'day-banner');
  const intro = element('div', 'day-intro');
  intro.append(element('p','eyebrow',`DAY ${index+1} / ${day.area}`),element('h3','',day.title),element('p','',day.summary));
  const meta = element('div','day-meta');
  meta.append(element('span','chip',day.transport));
  for (const id of day.lodging) {
    const place = placeById(id);
    const link = publicLink(place.name,place.mapUrl,'chip lodging-link');
    link.setAttribute('aria-label',`住宿：${place.name}，Google Maps（另開分頁）`);
    meta.append(link);
  }
  intro.append(meta);
  const photo = element('img','day-photo');
  photo.src = day.image;
  photo.alt = day.imageAlt;
  photo.width = 800; photo.height = 500;
  banner.append(intro,photo);
  panel.append(banner);
  const stops = element('div','day-stops');
  for (const stop of day.stops) {
    const row = element('article','stop');
    row.append(element('div','stop-time',stop.period));
    const card = element('div','stop-card');
    const copy = element('div');
    copy.append(element('h4','',stop.name),element('p','',stop.note));
    const place = stop.placeId ? placeById(stop.placeId) : null;
    if (place) copy.append(element('p','place-address',place.address));
    if (place?.imageCaption) copy.append(element('p','photo-note',place.imageCaption));
    if (stop.status !== 'planned') copy.append(badge(stop.status));
    const image=placePhoto(place,'stop-photo');
    if(image)card.append(image); else card.classList.add('without-photo');
    card.append(copy);
    const actions = element('div','stop-actions');
    if (place) actions.append(mapLink(place));
    if (stop.url) actions.append(publicLink('官方資訊',stop.url));
    card.append(actions);row.append(card);stops.append(row);
  }
  panel.append(stops,element('p','day-note',day.note));
  if (focus) $(`#tab-${day.id}`).focus();
}
function renderTabs() {
  const tabs = $('#day-tabs');
  trip.days.forEach((day,index) => {
    const button = element('button','day-tab');
    button.type='button'; button.id=`tab-${day.id}`;
    button.setAttribute('role','tab'); button.setAttribute('aria-controls','day-panel');
    button.append(element('strong','',`Day ${index+1}`),element('span','',day.shortTitle));
    button.addEventListener('click',()=>renderDay(index));
    button.addEventListener('keydown',(event)=>{
      let next;
      if (event.key==='ArrowRight') next=(currentDay+1)%trip.days.length;
      if (event.key==='ArrowLeft') next=(currentDay-1+trip.days.length)%trip.days.length;
      if (event.key==='Home') next=0;
      if (event.key==='End') next=trip.days.length-1;
      if(next!==undefined){event.preventDefault();renderDay(next,true);}
    });
    tabs.append(button);
  });
}
function renderTasks() {
  const list=$('#task-list'); list.replaceChildren();
  const tasks=trip.checklist.filter(task=>ownerFilter==='all'||task.owners.includes(ownerFilter));
  $('#task-summary').textContent=`${tasks.length} 項安排`;
  for(const task of tasks){
    const card=element('article','task-card');
    const top=element('div','task-top');
    top.append(element('span','owner',task.owners.join(' / ')),badge(task.status));
    card.append(top,element('h3','',task.title),element('p','',task.note));
    if(task.url)card.append(publicLink('查看參考資訊',task.url));
    list.append(card);
  }
}
function renderFilters(){
  for(const [value,label] of [['all','全部'],['Leo','Leo'],['Tyson','Tyson']]){
    const button=element('button','filter',label);button.type='button';
    button.setAttribute('aria-pressed',String(value===ownerFilter));
    button.addEventListener('click',()=>{ownerFilter=value;document.querySelectorAll('.filter').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));renderTasks();});
    $('#task-filters').append(button);
  }
}
function renderPlaces(){
  const query=$('#place-search').value.trim().toLocaleLowerCase();
  const list=$('#place-list');list.replaceChildren();
  const matches=trip.places.filter(place=>(placeCategory==='all'||(placeCategory==='自然'?['海灘','景點','自然'].includes(place.category):place.category===placeCategory))&&`${place.name} ${place.area} ${place.note} ${place.address}`.toLocaleLowerCase().includes(query));
  const filtered=Boolean(query)||placeCategory!=='all';
  const places=filtered||showAllPlaces?matches:['gojump','hanauma','kualoa','dolphins'].map(placeById);
  $('#places-title').textContent=filtered?'探索收藏':showAllPlaces?'所有景點收藏':'想去的地方';
  $('#place-count').textContent=filtered?`${matches.length} 個符合的地點`:`${showAllPlaces?trip.places.length:4} 個${showAllPlaces?'地點':'精選活動'}`;
  $('#show-all-places').textContent=showAllPlaces&&!filtered?'顯示精選':'查看全部收藏';
  $('#clear-place-filters').hidden=!filtered;
  for(const button of document.querySelectorAll('.category-button'))button.setAttribute('aria-pressed',String(button.dataset.category===placeCategory));
  $('#place-empty').hidden=places.length>0;
  for(const place of places){
    const card=element('article','place-card');
    const image=placePhoto(place,'place-photo');
    if(image){
      const link=publicLink('',place.mapUrl,'card-image');link.setAttribute('aria-label',`${place.name}：查看 Google Maps（另開分頁）`);link.append(image);card.append(link);
    }
    const body=element('div','card-body');
    body.append(element('span','place-category',`${place.area} / ${place.category}`),element('h3','',place.name),element('p','',place.note),element('p','place-address',place.address),mapLink(place));
    if (place.imageCaption) body.insertBefore(element('p','photo-note',place.imageCaption),body.lastChild);
    card.append(body);
    list.append(card);
  }
}
function clearPlaceFilters(){
  placeCategory='all';$('#place-search').value='';$('#hero-query').value='';
}
function selectNav(target){
  document.querySelectorAll('.header nav a').forEach(a=>a.classList.toggle('active',a.getAttribute('href')===target));
}
function renderCategories(){
  for(const category of categories){
    const button=element('button','category-button');button.type='button';button.dataset.category=category.value;button.setAttribute('aria-pressed','false');
    const tile=element('span','category-icon');tile.style.backgroundColor=category.color;tile.append(icon(category.icon));
    button.append(tile,element('strong','',category.name));
    button.addEventListener('click',()=>{placeCategory=placeCategory===category.value?'all':category.value;showAllPlaces=true;renderPlaces();selectNav('#places');$('#places').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
    $('#categories').append(button);
  }
}
async function init(){
  try{
    const response=await fetch('./data/trip.json');
    if(!response.ok)throw new Error('Trip data unavailable');
    trip=await response.json();
    if(!Array.isArray(trip.days)||trip.days.length!==8)throw new Error('Invalid trip data');
    renderTabs();renderDay(0);renderFilters();renderTasks();renderCategories();renderPlaces();
    $('#place-search').addEventListener('input',renderPlaces);
    $('#hero-search').addEventListener('submit',event=>{event.preventDefault();$('#place-search').value=$('#hero-query').value;placeCategory='all';showAllPlaces=true;renderPlaces();selectNav('#places');$('#places').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
    $('#show-all-places').addEventListener('click',()=>{const filtered=placeCategory!=='all'||$('#place-search').value.trim();showAllPlaces=filtered||!showAllPlaces;clearPlaceFilters();renderPlaces();});
    $('#clear-place-filters').addEventListener('click',()=>{clearPlaceFilters();showAllPlaces=true;renderPlaces();});
    for(const link of document.querySelectorAll('.header a'))link.addEventListener('click',()=>selectNav(link.getAttribute('href')==='#top'?'#itinerary':link.getAttribute('href')));
    for(const resource of trip.resources){
      const card=element('article','resource');
      card.append(element('h3','',resource.title),element('p','',resource.note),publicLink('前往官方網站',resource.url,''));
      $('#resource-list').append(card);
    }
  }catch(error){$('#load-error').hidden=false;console.error('Unable to load public itinerary.');}
}
init();
