f = open('jutilan-kiekkokoulu.html', 'r', encoding='utf-8')
html = f.read()
f.close()

# Etsi renderDivisions funktion alku ja loppu
alku = html.find("function renderDivisions() {")
if alku == -1:
    print("EI LOYDY!")
else:
    # Etsi funktion loppu - sulkeva }
    syvyys = 0
    loppu = alku
    for i, c in enumerate(html[alku:]):
        if c == '{': syvyys += 1
        elif c == '}': 
            syvyys -= 1
            if syvyys == 0:
                loppu = alku + i + 1
                break
    print("Funktio loydetty, pituus:", loppu - alku)
    print("Korvataan...")
    
    uusi = """function renderDivisions() {
  const now = new Date();
  const d = new Date(now.getFullYear(), now.getMonth() + monthOffset, 1);
  const monthsFI = ['TAMMIKUU','HELMIKUU','MAALISKUU','HUHTIKUU','TOUKOKUU','KESÄKUU','HEINÄKUU','ELOKUU','SYYSKUU','LOKAKUU','MARRASKUU','JOULUKUU'];
  const monthKey = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0');
  document.getElementById('div-month').textContent = monthsFI[d.getMonth()] + ' ' + d.getFullYear();
  state.users.forEach(u => u.divisionThisMonth = getDivisionForMonth(u, monthKey));
  const allUsers = state.users.map(u => ({...u, pts: calcMonthPoints(u, monthOffset)})).sort((a,b) => b.pts - a.pts);
  const globalMax = allUsers.length ? allUsers[0].pts : 0;
  allUsers.forEach((u,i) => { u.kkRank = i+1; });
  document.getElementById('month-leader-pts').textContent = globalMax.toLocaleString('fi-FI');
  document.getElementById('month-teams').textContent = allUsers.length;
  const avg = allUsers.length ? Math.round(allUsers.reduce((s,u) => s+u.pts,0)/allUsers.length) : 0;
  document.getElementById('month-avg').textContent = avg.toLocaleString('fi-FI');
  const container = document.getElementById('divisions-container');
  if (state.users.length === 0) { container.innerHTML = '<div class="empty-state"><p>Ei joukkueita</p></div>'; return; }
  container.innerHTML = DIVISION_ORDER.map(divKey => {
    const cfg = DIVISION_CONFIG[divKey];
    const divUsers = allUsers.filter(u => u.divisionThisMonth === divKey).sort((a,b) => b.pts - a.pts);
    if (!divUsers.length) return '';
    const divMax = divUsers[0].pts;
    const relegateStart = divUsers.length - cfg.relegateN;
    return '<div class="kk-section"><div class="kk-division-header ' + cfg.cls + '">' + cfg.label + '</div>' +
      '<div class="card" style="padding:0;overflow:hidden"><table class="kk-table">' +
      '<thead><tr><th>#</th><th>Joukkue</th><th style="text-align:right">Pisteet</th><th style="text-align:right">KK#</th><th style="text-align:right">Plussaa</th><th style="text-align:right">€€€</th><th style="text-align:right">Jatko</th></tr></thead><tbody>' +
      divUsers.map((u,i) => {
        const rank = i+1;
        const plus = u.pts - divMax;
        const prize = cfg.prize[rank] || '';
        let jatko = '>', jatkoCls = 'stay';
        if (divKey==='Ykkonen' && rank > divUsers.length - cfg.relegateN) { jatko='↓ Kakkonen'; jatkoCls='down'; }
        else if (divKey==='Kakkonen' && rank <= cfg.promoteN) { jatko='↑ Ykkonen'; jatkoCls='up'; }
        else if (divKey==='Kakkonen' && rank > divUsers.length - cfg.relegateN) { jatko='↓ Kolmonen'; jatkoCls='down'; }
        else if (divKey==='Kolmonen' && rank <= cfg.promoteN) { jatko='↑ Kakkonen'; jatkoCls='up'; }
        const rowCls = (divKey!=='Ykkonen' && rank<=cfg.promoteN) ? 'promote' : (cfg.relegateN>0 && rank>relegateStart) ? 'relegate' : '';
        return '<tr class="' + rowCls + '"><td><span class="kk-rank' + (rank<=3?' r'+rank:'') + '">' + rank + '</span></td>' +
          '<td><div style="font-weight:600">' + (u.espnTeamName||u.name) + '</div><div style="font-size:11px;color:var(--muted)">' + u.name + '</div></td>' +
          '<td class="kk-pts">' + u.pts.toLocaleString('fi-FI') + '</td>' +
          '<td class="kk-kknum">' + u.kkRank + '</td>' +
          '<td class="kk-plus ' + (plus===0?'zero':'neg') + '">' + (plus===0?'0':plus.toLocaleString('fi-FI')) + '</td>' +
          '<td class="kk-prize">' + prize + '</td>' +
          '<td class="kk-jatko ' + jatkoCls + '">' + jatko + '</td></tr>';
      }).join('') + '</tbody></table></div></div>';
  }).join('');
}"""
    
    html = html[:alku] + uusi + html[loppu:]
    f = open('jutilan-kiekkokoulu.html', 'w', encoding='utf-8')
    f.write(html)
    f.close()
    print("Valmis! Koko:", len(html))