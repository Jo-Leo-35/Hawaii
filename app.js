const $ = (selector) => document.querySelector(selector);
const statusLabels = {planned:'行程安排',pending:'待確認',confirmed:'已安排',optional:'候選備案'};
let trip;
let currentDay = 0;
let ownerFilter = 'all';

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function badge(status) { return element('span', `status status-${status}`, statusLabels[status] || statusLabels.planned); }
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
function mapLink(query) {
  const url = new URL('https://www.google.com/maps/search/');
  url.searchParams.set('api', '1');
  url.searchParams.set('query', query);
  const link = publicLink('Google Maps', url.href, 'map-link');
  link.setAttribute('aria-label', `${query}：Google Maps（另開分頁）`);
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
  meta.append(element('span','chip',day.transport),element('span','chip','住宿區域：Waikiki'));
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
    const copy = element('div');
    copy.append(element('h4','',stop.name),element('p','',stop.note));
    if (stop.status !== 'planned') copy.append(badge(stop.status));
    row.append(copy);
    const actions = element('div','stop-actions');
    if (stop.mapQuery) actions.append(mapLink(stop.mapQuery));
    if (stop.url) actions.append(publicLink('官方資訊',stop.url));
    row.append(actions); stops.append(row);
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
  for(const [value,label] of [['all','全部'],['Leon','Leon'],['Tyson','Tyson']]){
    const button=element('button','filter',label);button.type='button';
    button.setAttribute('aria-pressed',String(value===ownerFilter));
    button.addEventListener('click',()=>{ownerFilter=value;document.querySelectorAll('.filter').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));renderTasks();});
    $('#task-filters').append(button);
  }
}
function renderPlaces(){
  const query=$('#place-search').value.trim().toLocaleLowerCase();
  const list=$('#place-list');list.replaceChildren();
  const places=trip.places.filter(place=>`${place.name} ${place.area} ${place.note}`.toLocaleLowerCase().includes(query));
  $('#place-empty').hidden=places.length>0;
  for(const place of places){
    const card=element('article','place-card');
    card.append(element('span','',`${place.area} / ${place.category}`),element('h3','',place.name),element('p','',place.note),mapLink(place.mapQuery));
    list.append(card);
  }
}
async function init(){
  try{
    const response=await fetch('./data/trip.json');
    if(!response.ok)throw new Error('Trip data unavailable');
    trip=await response.json();
    if(!Array.isArray(trip.days)||trip.days.length!==8)throw new Error('Invalid trip data');
    renderTabs();renderDay(0);renderFilters();renderTasks();renderPlaces();
    $('#place-search').addEventListener('input',renderPlaces);
    for(const resource of trip.resources){
      const card=element('article','resource');
      card.append(element('h3','',resource.title),element('p','',resource.note),publicLink('前往官方網站',resource.url,''));
      $('#resource-list').append(card);
    }
  }catch(error){$('#load-error').hidden=false;console.error('Unable to load public itinerary.');}
}
init();
