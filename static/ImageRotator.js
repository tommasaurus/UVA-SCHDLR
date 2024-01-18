window.onload = function() {
    var images = ['/static/images/rotunda1.png', '/static/images/rotunda2.png', '/static/images/rotunda3.png', '/static/images/rotunda4.png', '/static/images/rotunda5.png', '/static/images/rotunda6.png', '/static/images/rotunda7.png', '/static/images/rotunda8.png', '/static/images/rotunda9.png', '/static/images/rotunda10.png', '/static/images/rotunda11.png', '/static/images/rotunda12.png', '/static/images/rotunda13.png', '/static/images/rotunda14.png'];
    function changeImage() { 
        var randomIndex = Math.floor(Math.random() * images.length);
        document.getElementById('randomImage').src = images[randomIndex];
    }
    changeImage();
    setInterval(changeImage, 5000); // Change image every 5000 milliseconds (5 seconds)
};