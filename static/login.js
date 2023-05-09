var firstsec = document.getElementById('one');
var secondsec = document.getElementById('two');
document.onscroll = function scroll() {
  secondsec.scrollIntoView({behavior: "smooth"});
 }