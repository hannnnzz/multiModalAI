// Register GSAP plugins
gsap.registerPlugin(ScrambleTextPlugin, MorphSVGPlugin);

// Constants
const BLINK_SPEED = 0.075;
const TOGGLE_SPEED = 0.125;
const ENCRYPT_SPEED = 1;
const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~,.<>?/;":][}{+_)(*&^%$#@!±=-§';

// State
let busy = false;
let blinkTl;
let reset;

// DOM Elements
const EYES = document.querySelectorAll('.eye');
const TOGGLES = document.querySelectorAll('.eye-toggle');
const INPUTS = {
    password: document.querySelector('#password'),
    confirm: document.querySelector('#confirmpassword')
};
const PROXY = document.createElement('div');

// Blink animation
const blink = () => {
    const delay = gsap.utils.random(2, 8);
    const duration = BLINK_SPEED;
    const repeat = Math.random() > 0.5 ? 3 : 1;

    blinkTl = gsap.timeline({
            delay,
            onComplete: () => blink(),
            repeat,
            yoyo: true
        })
        .to('.lid--upper', {
            morphSVG: '.lid--lower',
            duration
        })
        .to('#eye-open path', {
            morphSVG: '#eye-closed path',
            duration
        }, 0);
};

// Initialize blinking
blink();

// Eye movement
const posMapper = gsap.utils.mapRange(-100, 100, 30, -30);

const moveEye = ({ x, y }) => {
    if (reset) reset.kill();

    reset = gsap.delayedCall(2, () => {
        gsap.to('.eye', {
            xPercent: 0,
            yPercent: 0,
            duration: 0.2
        });
    });

    EYES.forEach(eye => {
        const BOUNDS = eye.getBoundingClientRect();
        gsap.set(eye, {
            xPercent: gsap.utils.clamp(-30, 30, posMapper(BOUNDS.x - x)),
            yPercent: gsap.utils.clamp(-30, 30, posMapper(BOUNDS.y - y))
        });
    });
};

window.addEventListener('pointermove', moveEye);

// Toggle password visibility
TOGGLES.forEach((toggle, index) => {
    const input = index === 0 ? INPUTS.password : INPUTS.confirm;

    toggle.addEventListener('click', () => {
        if (busy) return;

        const isText = input.matches('[type=password]');
        const val = input.value;
        busy = true;
        toggle.setAttribute('aria-pressed', isText);
        const duration = TOGGLE_SPEED;

        if (isText) {
            if (blinkTl) blinkTl.kill();

            gsap.timeline({
                    onComplete: () => {
                        busy = false;
                    }
                })
                .to('.lid--upper', {
                    morphSVG: '.lid--lower',
                    duration
                })
                .to('#eye-open path', {
                    morphSVG: '#eye-closed path',
                    duration
                }, 0)
                .to(PROXY, {
                    duration: ENCRYPT_SPEED,
                    onStart: () => {
                        input.type = 'text';
                    },
                    onComplete: () => {
                        PROXY.innerHTML = '';
                        input.value = val;
                    },
                    scrambleText: {
                        chars,
                        text: val.charAt(val.length - 1) === ' ' ?
                            `${val.slice(0, val.length - 1)}${chars.charAt(
                                Math.floor(Math.random() * chars.length))}` : val
                    },
                    onUpdate: () => {
                        const len = val.length - PROXY.innerText.length;
                        input.value = `${PROXY.innerText}${new Array(len).fill('•').join('')}`;
                    }
                }, 0);
        } else {
            gsap.timeline({
                    onComplete: () => {
                        blink();
                        busy = false;
                    }
                })
                .to('.lid--upper', {
                    morphSVG: '.lid--upper',
                    duration
                })
                .to('#eye-open path', {
                    morphSVG: '#eye-open path',
                    duration
                }, 0)
                .to(PROXY, {
                    duration: ENCRYPT_SPEED,
                    onComplete: () => {
                        input.type = 'password';
                        input.value = val;
                        PROXY.innerHTML = '';
                    },
                    scrambleText: {
                        chars,
                        text: new Array(val.length).fill('•').join('')
                    },
                    onUpdate: () => {
                        input.value = `${PROXY.innerText}${val.slice(
                            PROXY.innerText.length,
                            val.length)}`;
                    }
                }, 0);
        }
    });
});

// Form validation
document.querySelector('form').addEventListener('submit', function(event) {
    const password = document.querySelector('input[name="password"]').value;
    const confirmPassword = document.querySelector('input[name="confirm_password"]').value;

    if (password !== confirmPassword) {
        event.preventDefault();
        Swal.fire({
            toast: true,
            position: 'top',
            icon: 'error',
            title: 'Password tidak cocok!',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            width: '400px'
        });
    }
});
// Animasi untuk alert
if (document.querySelector('.alert')) {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        // Auto close setelah 5 detik
        setTimeout(() => {
            alert.classList.add('fade-out');
            setTimeout(() => alert.remove(), 500);
        }, 5000);

        // Close manual saat diklik
        alert.addEventListener('click', () => {
            alert.classList.add('fade-out');
            setTimeout(() => alert.remove(), 500);
        });
    });
}