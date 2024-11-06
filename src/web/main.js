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

    //requestAnimationFrame(animate);
});


function updateValue(value) {
    var bar = document.getElementById('bar');
    bar.style.transform = "rotate(" + (45 + (value * 1.8)) + "deg)";
}
eel.expose(updateValue);



function updateOBDData() {
    document.getElementById('engineLoad').textContent = Math.floor(Math.random() * 100);
    document.getElementById('coolantTemp').textContent = Math.floor(Math.random() * 120);
    document.getElementById('rpm').textContent = Math.floor(Math.random() * 7000);
    document.getElementById('throttlePosition').textContent = Math.floor(Math.random() * 100);
    document.getElementById('fuelLevel').textContent = Math.floor(Math.random() * 100);
    document.getElementById('intakeAirTemp').textContent = Math.floor(Math.random() * 50);
}

setInterval(updateOBDData, 1000); // Update every 1 second