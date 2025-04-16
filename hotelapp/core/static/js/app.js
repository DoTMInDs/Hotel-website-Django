

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
