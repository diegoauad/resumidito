const SECONDS_PER_DAY = 86400;
const HOURS_PER_DAY = 24;
const API_HOST = 'http://127.0.0.1:5000';

const secondsToHms = (seconds) => {
  const days = Math.floor(seconds / SECONDS_PER_DAY);
  const remainderSeconds = seconds % SECONDS_PER_DAY;
  const hms = new Date(remainderSeconds * 1000).toISOString().substring(11, 19);
  return hms.replace(/^(\d+)/, h => `${Number(h) + days * HOURS_PER_DAY}`.padStart(2, '0'));
};

function getPosition(string, subString, index) {
  return string.split(subString, index).join(subString).length;
}

const href = window.location.href;
var link = href.substring(getPosition(href, '/', 3) + 1);
if ( href.startsWith('file:///')) {
    var link = 'www.youtube.com/watch?v=FCGnP77xvrU';
}

oboe(`${API_HOST}/${link}`)
    .node('summary', function( summary ) {
        $('.loading-summary').remove();
        const p = document.createElement('p');
        p.id = 'summary-text';
        p.textContent = summary;
        $('#video-summary').append(p);
    })
    .node('chapters.*', function( chapter ) {
        const li = document.createElement('li');
        li.innerHTML = `
        <span>${secondsToHms(chapter.start)} - ${secondsToHms(chapter.end)}</span>
        <span>${chapter.title}</span>
        `;
        $('#chapters-list').append(li);
        $('.loading-chapters').remove();
    }
);