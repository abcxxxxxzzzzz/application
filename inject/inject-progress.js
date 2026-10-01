
(function () {
    "use strict";

    if (window.self === window.top) {
        return;
    }

    var progressStarted = false;
    var finishTimer = null;
    var lastRequestTime = 0;

    function notifyStart() {
        if (progressStarted) {
            return;
        }

        progressStarted = true;

        window.parent.postMessage({
            type: "page-progress-start"
        }, "*");
    }

    function notifyEnd() {
        if (!progressStarted) {
            return;
        }

        progressStarted = false;

        window.parent.postMessage({
            type: "page-progress-end"
        }, "*");
    }

    function networkActivity() {
        lastRequestTime = Date.now();

        notifyStart();

        clearTimeout(finishTimer);

        finishTimer = setTimeout(function () {
            if (Date.now() - lastRequestTime >= 300) {
                notifyEnd();
            }
        }, 350);
    }

    // =========================
    // 监听浏览器资源请求
    // =========================
    if (window.PerformanceObserver) {
        try {
            var observer = new PerformanceObserver(function (list) {
                var entries = list.getEntries();

                if (!entries.length) {
                    return;
                }

                networkActivity();
            });

            observer.observe({
                type: "resource",
                buffered: false
            });
        } catch (e) {
        }
    }

    // =========================
    // fetch
    // =========================
    if (window.fetch) {
        var originalFetch = window.fetch;

        window.fetch = function () {
            networkActivity();

            return originalFetch.apply(this, arguments);
        };
    }

    // =========================
    // XMLHttpRequest
    // =========================
    var originalSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.send = function () {
        networkActivity();

        return originalSend.apply(this, arguments);
    };

    // =========================
    // sendBeacon
    // =========================
    if (navigator.sendBeacon) {
        var originalBeacon = navigator.sendBeacon;

        navigator.sendBeacon = function () {
            networkActivity();

            return originalBeacon.apply(this, arguments);
        };
    }

    // =========================
    // iframe title
    // =========================
    function sendIframeTitle() {
        window.parent.postMessage({
            type: "iframe-title",
            title: document.title || ""
        }, "*");
    }

    sendIframeTitle();

    if (window.MutationObserver) {
        var title = document.querySelector("title");

        if (title) {
            new MutationObserver(function () {
                sendIframeTitle();
            }).observe(title, {
                childList: true,
                subtree: true,
                characterData: true
            });
        }
    }

    window.addEventListener("load", function () {
        sendIframeTitle();
    });

})();
