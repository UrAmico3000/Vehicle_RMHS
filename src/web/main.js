console.log("worked");

document.querySelectorAll(".progress").forEach((progress)=> {
    var bar = progress.querySelector(".bar");
    var val = progress.querySelector("span");
    var perc = parseInt(val.textContent, 10);
    
    var start =  0 ;
    var end =  perc ;

    var duration = 3000;
    var startTime = null;

    function animate(time) {
        if (!startTime) startTime = time;
        var progressTime = time - startTime;
        var percent = Math.min(progressTime / duration, 1);
        var p = start + (end - start) * percent;

        bar.style.transform = "rotate(" + (45 + (p * 1.8)) + "deg)";
        val.textContent = Math.floor(p);

        if (percent < 1) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);
});
