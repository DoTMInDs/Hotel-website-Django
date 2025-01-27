var slideImage = document.getElementById('slideImage');

var images = new Array(   
    "image/assets/backgorund2.jpg",
    "image/assets/backgorund3.jpg",
    "image/assets/room.jpg"
    // "image/assets/backgorund1.jpg",
);

var len = images.length;
var i = 0;

function slider() {
    if(i > len-1){
        i = 0;
    }
    slideImage.src = images[i];
    i++;
    setTimeout('slider()', 3000);
}

const mobileMenu = document.getElementById('mobile-menu');
const navLinks = document.getElementById('nav-links');

mobileMenu.addEventListener('click', () => {
    mobileMenu.classList.toggle('change');
    navLinks.classList.toggle('showing');
});



const viewPrices = document.querySelectorAll('.view_price');
const priceTag = document.getElementById('priceTag');

for (const viewPrice of viewPrices) {
    viewPrice.addEventListener('click', (e) =>{
        let priceTag = document.getElementById('priceTag-' +e.target.dataset.pk);
        priceTag.classList.toggle('active-price-tag')
    })
}


//------------- LOGIN-&-SIGN-UP-section----------------------//
