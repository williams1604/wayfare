// Wayfare Global State Manager for Static Host (GitHub Pages) & Client Interactivity

(function () {
    const defaultPackages = [
        {
            id: 1,
            name: "Swiss Alps Adventure",
            destination: "Switzerland",
            price: 185000,
            duration: "7 Days / 6 Nights",
            rating: 4.9,
            reviews_count: 128,
            image_url: "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?w=600&h=400&fit=crop",
            description: "Experience the majestic Swiss Alps with guided hiking, scenic train rides on the Glacier Express, and luxury mountain chalet stays.",
            is_bestseller: true,
            is_premium: true
        },
        {
            id: 2,
            name: "Kyoto Cherry Blossom Tour",
            destination: "Japan",
            price: 165000,
            duration: "6 Days / 5 Nights",
            rating: 4.8,
            reviews_count: 95,
            image_url: "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&h=400&fit=crop",
            description: "Immerse yourself in Japan's cultural heartland during sakura season. Visit historic temples, traditional tea houses, and bamboo groves.",
            is_bestseller: true,
            is_premium: false
        },
        {
            id: 3,
            name: "Amalfi Coast Dream",
            destination: "Italy",
            price: 195000,
            duration: "8 Days / 7 Nights",
            rating: 4.9,
            reviews_count: 142,
            image_url: "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=600&h=400&fit=crop",
            description: "Cliffside luxury along Italy's spectacular coastline. Private boat tours to Capri, wine tasting in Ravello, and authentic Mediterranean cuisine.",
            is_bestseller: false,
            is_premium: true
        },
        {
            id: 4,
            name: "Santorini Sunset Retreat",
            destination: "Greece",
            price: 145000,
            duration: "5 Days / 4 Nights",
            rating: 4.7,
            reviews_count: 88,
            image_url: "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=600&h=400&fit=crop",
            description: "Whitewashed villas, crystal-clear Aegean waters, and world-famous sunsets in Oia.",
            is_bestseller: true,
            is_premium: false
        },
        {
            id: 5,
            name: "Bali Tropical Paradise",
            destination: "Indonesia",
            price: 95000,
            duration: "6 Days / 5 Nights",
            rating: 4.8,
            reviews_count: 110,
            image_url: "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&h=400&fit=crop",
            description: "Spiritual wellness, lush rice terraces in Ubud, private beach club access, and iconic water temples.",
            is_bestseller: false,
            is_premium: false
        },
        {
            id: 6,
            name: "Dubai Luxury Experience",
            destination: "UAE",
            price: 175000,
            duration: "5 Days / 4 Nights",
            rating: 4.9,
            reviews_count: 156,
            image_url: "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&h=400&fit=crop",
            description: "5-star luxury in the desert metropolis. VIP Burj Khalifa entry, desert safari with private dinner, and luxury yacht cruise.",
            is_bestseller: true,
            is_premium: true
        }
    ];

    const defaultBookings = [
        {
            id: 101,
            user_email: "john@example.com",
            first_name: "John",
            last_name: "Doe",
            phone: "+1 555-0199",
            destination: "Swiss Alps Adventure",
            package_id: 1,
            date: "2026-09-15",
            end_date: "2026-09-21",
            travelers: 2,
            special_requests: "Honeymoon setup preferred.",
            status: "Confirmed",
            payment_method: "Credit Card",
            transaction_id: "TXN-998241",
            total_amount: 370000,
            created_at: "2026-08-25"
        },
        {
            id: 102,
            user_email: "john@example.com",
            first_name: "John",
            last_name: "Doe",
            phone: "+1 555-0199",
            destination: "Kyoto Cherry Blossom Tour",
            package_id: 2,
            date: "2026-10-10",
            end_date: "2026-10-16",
            travelers: 1,
            special_requests: "Vegetarian meal plan.",
            status: "Pending",
            payment_method: "GPay UPI",
            transaction_id: "UPI-449120",
            total_amount: 165000,
            created_at: "2026-08-28"
        }
    ];

    const defaultEnquiries = [
        {
            id: 1,
            user_email: "john@example.com",
            name: "John Doe",
            email: "john@example.com",
            subject: "Group Booking Discount Inquiry",
            message: "Hello, we have a group of 8 people interested in the Amalfi Coast tour. Do you offer corporate or group discounts?",
            status: "Responded",
            response: "Hi John, yes! For groups of 6 or more, we offer a 12% group discount along with private transport upgrade.",
            created_at: "2026-08-24"
        }
    ];

    const defaultReviews = [
        {
            id: 1,
            user_name: "Jennifer Davis",
            user_email: "jennifer@example.com",
            package_id: 2,
            package_name: "Kyoto Cherry Blossom Tour",
            rating: 5,
            comment: "Our trip to Japan was absolutely flawless! Every detail was perfectly planned, and the local experiences were authentic and memorable.",
            is_approved: true
        },
        {
            id: 2,
            user_name: "Marcus Johnson",
            user_email: "marcus@example.com",
            package_id: 1,
            package_name: "Swiss Alps Adventure",
            rating: 5,
            comment: "The team went above and beyond to accommodate our special requests. Outstanding customer service!",
            is_approved: true
        }
    ];

    // Initializer
    if (!localStorage.getItem('wayfare_packages')) {
        localStorage.setItem('wayfare_packages', JSON.stringify(defaultPackages));
    }
    if (!localStorage.getItem('wayfare_bookings')) {
        localStorage.setItem('wayfare_bookings', JSON.stringify(defaultBookings));
    }
    if (!localStorage.getItem('wayfare_enquiries')) {
        localStorage.setItem('wayfare_enquiries', JSON.stringify(defaultEnquiries));
    }
    if (!localStorage.getItem('wayfare_reviews')) {
        localStorage.setItem('wayfare_reviews', JSON.stringify(defaultReviews));
    }

    window.WayfareState = {
        getCurrentUser: function () {
            const raw = localStorage.getItem('wayfare_user');
            return raw ? JSON.parse(raw) : null;
        },
        setCurrentUser: function (user) {
            if (user) {
                localStorage.setItem('wayfare_user', JSON.stringify(user));
            } else {
                localStorage.removeItem('wayfare_user');
            }
            this.updateHeaderNav();
        },
        logout: function () {
            localStorage.removeItem('wayfare_user');
            window.location.href = 'index.html';
        },
        getPackages: function () {
            return JSON.parse(localStorage.getItem('wayfare_packages') || '[]');
        },
        addPackage: function (pkg) {
            const pkgs = this.getPackages();
            pkg.id = pkgs.length ? Math.max(...pkgs.map(p => p.id)) + 1 : 1;
            pkgs.push(pkg);
            localStorage.setItem('wayfare_packages', JSON.stringify(pkgs));
            return pkg;
        },
        getBookings: function (userEmail = null) {
            const all = JSON.parse(localStorage.getItem('wayfare_bookings') || '[]');
            if (userEmail) {
                return all.filter(b => b.user_email === userEmail);
            }
            return all;
        },
        addBooking: function (booking) {
            const bookings = JSON.parse(localStorage.getItem('wayfare_bookings') || '[]');
            booking.id = bookings.length ? Math.max(...bookings.map(b => b.id)) + 1 : 101;
            booking.created_at = new Date().toISOString().split('T')[0];
            booking.status = booking.status || 'Pending';
            bookings.push(booking);
            localStorage.setItem('wayfare_bookings', JSON.stringify(bookings));
            return booking;
        },
        updateBookingStatus: function (id, status) {
            const bookings = JSON.parse(localStorage.getItem('wayfare_bookings') || '[]');
            const b = bookings.find(item => item.id == id);
            if (b) {
                b.status = status;
                localStorage.setItem('wayfare_bookings', JSON.stringify(bookings));
            }
        },
        deleteBooking: function (id) {
            let bookings = JSON.parse(localStorage.getItem('wayfare_bookings') || '[]');
            bookings = bookings.filter(b => b.id != id);
            localStorage.setItem('wayfare_bookings', JSON.stringify(bookings));
        },
        getEnquiries: function (userEmail = null) {
            const all = JSON.parse(localStorage.getItem('wayfare_enquiries') || '[]');
            if (userEmail) {
                return all.filter(e => e.user_email === userEmail || e.email === userEmail);
            }
            return all;
        },
        addEnquiry: function (enq) {
            const enqs = JSON.parse(localStorage.getItem('wayfare_enquiries') || '[]');
            enq.id = enqs.length ? Math.max(...enqs.map(e => e.id)) + 1 : 1;
            enq.status = 'Pending';
            enq.created_at = new Date().toISOString().split('T')[0];
            enqs.push(enq);
            localStorage.setItem('wayfare_enquiries', JSON.stringify(enqs));
            return enq;
        },
        respondEnquiry: function (id, response) {
            const enqs = JSON.parse(localStorage.getItem('wayfare_enquiries') || '[]');
            const e = enqs.find(item => item.id == id);
            if (e) {
                e.response = response;
                e.status = 'Responded';
                localStorage.setItem('wayfare_enquiries', JSON.stringify(enqs));
            }
        },
        deleteEnquiry: function (id) {
            let enqs = JSON.parse(localStorage.getItem('wayfare_enquiries') || '[]');
            enqs = enqs.filter(e => e.id != id);
            localStorage.setItem('wayfare_enquiries', JSON.stringify(enqs));
        },
        getReviews: function (approvedOnly = false) {
            const all = JSON.parse(localStorage.getItem('wayfare_reviews') || '[]');
            if (approvedOnly) {
                return all.filter(r => r.is_approved);
            }
            return all;
        },
        addReview: function (rev) {
            const revs = JSON.parse(localStorage.getItem('wayfare_reviews') || '[]');
            rev.id = revs.length ? Math.max(...revs.map(r => r.id)) + 1 : 1;
            rev.is_approved = false;
            revs.push(rev);
            localStorage.setItem('wayfare_reviews', JSON.stringify(revs));
            return rev;
        },
        toggleReviewApproval: function (id) {
            const revs = JSON.parse(localStorage.getItem('wayfare_reviews') || '[]');
            const r = revs.find(item => item.id == id);
            if (r) {
                r.is_approved = !r.is_approved;
                localStorage.setItem('wayfare_reviews', JSON.stringify(revs));
            }
        },
        deleteReview: function (id) {
            let revs = JSON.parse(localStorage.getItem('wayfare_reviews') || '[]');
            revs = revs.filter(r => r.id != id);
            localStorage.setItem('wayfare_reviews', JSON.stringify(revs));
        },
        updateHeaderNav: function () {
            this.ensureModalsExist();
            const navUserArea = document.getElementById('nav-user-area');
            if (!navUserArea) return;

            const user = this.getCurrentUser();
            if (user) {
                navUserArea.innerHTML = `
                    <div class="flex items-center gap-4">
                        <span class="text-sm font-medium text-[#2D3142]">Hello, ${escapeHTML(user.name)}</span>
                        ${user.role === 'admin'
                        ? `<a href="admin.html" class="text-sm font-medium text-[#FF6B35]">Admin Panel</a>`
                        : `<a href="dashboard.html" class="text-sm font-medium text-[#FF6B35]">Dashboard</a>`
                    }
                        <button onclick="WayfareState.logout()" class="text-sm font-medium text-[#6B7280] hover:text-[#FF6B35]">Logout</button>
                    </div>
                `;
            } else {
                navUserArea.innerHTML = `
                    <button onclick="openLoginModal(event)"
                      class="hidden md:block px-7 py-3.5 text-sm font-medium text-[#FF6B35] border-2 border-[#FF6B35] rounded-lg mr-4 hover:bg-[#FF6B35] hover:text-white transition-colors">
                      Login
                    </button>
                    <a href="packages.html" class="px-7 py-3.5 text-sm font-medium text-white bg-[#FF6B35] rounded-lg hover:bg-[#e55a2b] transition-colors shadow-md">
                      Book Now
                    </a>
                `;
            }
        },
        ensureModalsExist: function () {
            if (!document.getElementById('loginModal')) {
                const loginDiv = document.createElement('div');
                loginDiv.id = 'loginModal';
                loginDiv.className = 'hidden fixed inset-0 z-[100] flex items-center justify-center p-4';
                loginDiv.innerHTML = `
                    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" onclick="closeLoginModal()"></div>
                    <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden p-6 z-10">
                      <div class="flex justify-between items-center mb-6">
                        <h3 class="text-2xl font-bold text-[#2D3142]">Sign In</h3>
                        <button onclick="closeLoginModal()" class="text-gray-400 hover:text-gray-600">
                          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                      <form id="loginForm" onsubmit="submitLogin(event)" class="space-y-4">
                        <div>
                          <label class="block text-xs font-semibold text-gray-600 mb-1">Email</label>
                          <input type="email" id="loginEmail" required class="w-full px-4 py-3 border rounded-xl text-sm" placeholder="john@example.com / admin@wayfare.com" />
                        </div>
                        <div>
                          <label class="block text-xs font-semibold text-gray-600 mb-1">Password</label>
                          <input type="password" id="loginPassword" required class="w-full px-4 py-3 border rounded-xl text-sm" placeholder="••••••••" />
                        </div>
                        <button type="submit" class="w-full bg-[#FF6B35] text-white font-bold py-3.5 rounded-xl hover:bg-[#e55a2b] transition-colors shadow-lg">
                          Sign In
                        </button>
                        <p class="text-center text-xs text-gray-500 mt-4">
                          Demo Admin: <span class="font-semibold text-gray-700">admin@wayfare.com</span> (Pass: admin123)
                        </p>
                      </form>
                    </div>
                `;
                document.body.appendChild(loginDiv);
            }

            if (!document.getElementById('bookingModal')) {
                const bkgDiv = document.createElement('div');
                bkgDiv.id = 'bookingModal';
                bkgDiv.className = 'hidden fixed inset-0 z-[100] flex items-center justify-center p-4';
                bkgDiv.innerHTML = `
                    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" onclick="closeBookingModal()"></div>
                    <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden p-6 z-10">
                      <div class="flex justify-between items-center mb-6">
                        <h3 class="text-xl font-bold text-[#2D3142]">Book <span id="modalPkgTitle" class="text-[#FF6B35]"></span></h3>
                        <button onclick="closeBookingModal()" class="text-gray-400 hover:text-gray-600">
                          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                      <form id="bookingForm" onsubmit="submitBooking(event)" class="space-y-4">
                        <input type="hidden" id="modalPkgId" />
                        <input type="hidden" id="modalPkgName" />
                        <div class="grid grid-cols-2 gap-4">
                          <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">First Name</label>
                            <input type="text" id="bkgFirstName" required class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="John" />
                          </div>
                          <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Last Name</label>
                            <input type="text" id="bkgLastName" required class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="Doe" />
                          </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                          <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Email</label>
                            <input type="email" id="bkgEmail" required class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="john@example.com" />
                          </div>
                          <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Phone</label>
                            <input type="tel" id="bkgPhone" required class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="+1 (555) 123-4567" />
                          </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                          <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Travel Date</label>
                            <input type="date" id="bkgDate" required class="w-full px-3 py-2 border rounded-lg text-sm" />
                          </div>
                          <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Travelers</label>
                            <input type="number" id="bkgTravelers" min="1" max="20" value="2" required class="w-full px-3 py-2 border rounded-lg text-sm" />
                          </div>
                        </div>
                        <div>
                          <label class="block text-xs font-semibold text-gray-600 mb-1">Special Requests</label>
                          <textarea id="bkgRequests" rows="2" class="w-full px-3 py-2 border rounded-lg text-sm" placeholder="Meal preferences, room type..."></textarea>
                        </div>
                        <button type="submit" class="w-full bg-[#FF6B35] text-white font-bold py-3.5 rounded-xl hover:bg-[#e55a2b] transition-colors shadow-lg">
                          Proceed to Payment &rarr;
                        </button>
                      </form>
                    </div>
                `;
                document.body.appendChild(bkgDiv);
            }
        }
    };

    window.openLoginModal = function (e) {
        if (e && e.preventDefault) e.preventDefault();
        WayfareState.ensureModalsExist();
        const m = document.getElementById('loginModal');
        if (m) m.classList.remove('hidden');
    };

    window.closeLoginModal = function () {
        const m = document.getElementById('loginModal');
        if (m) m.classList.add('hidden');
    };

    window.submitLogin = function (e) {
        if (e && e.preventDefault) e.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const role = email.toLowerCase().includes('admin') ? 'admin' : 'user';
        const name = email.split('@')[0];

        WayfareState.setCurrentUser({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            email: email,
            role: role
        });

        window.closeLoginModal();
        if (role === 'admin') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'dashboard.html';
        }
    };

    window.openBookingModal = function (pkgId, pkgName) {
        WayfareState.ensureModalsExist();
        const modalPkgId = document.getElementById('modalPkgId');
        const modalPkgName = document.getElementById('modalPkgName');
        const modalPkgTitle = document.getElementById('modalPkgTitle');
        if (modalPkgId) modalPkgId.value = pkgId || '';
        if (modalPkgName) modalPkgName.value = pkgName || '';
        if (modalPkgTitle) modalPkgTitle.textContent = pkgName || 'Package';

        const user = WayfareState.getCurrentUser();
        if (user) {
            const bkgEmail = document.getElementById('bkgEmail');
            const bkgFirstName = document.getElementById('bkgFirstName');
            const bkgLastName = document.getElementById('bkgLastName');
            if (bkgEmail) bkgEmail.value = user.email || '';
            if (bkgFirstName) bkgFirstName.value = user.name.split(' ')[0] || '';
            if (bkgLastName) bkgLastName.value = user.name.split(' ')[1] || '';
        }

        const m = document.getElementById('bookingModal');
        if (m) m.classList.remove('hidden');
    };

    window.closeBookingModal = function () {
        const m = document.getElementById('bookingModal');
        if (m) m.classList.add('hidden');
    };

    window.submitBooking = function (e) {
        if (e && e.preventDefault) e.preventDefault();
        const pkgId = document.getElementById('modalPkgId').value;
        const pkgName = document.getElementById('modalPkgName').value;
        const firstName = document.getElementById('bkgFirstName').value;
        const lastName = document.getElementById('bkgLastName').value;
        const email = document.getElementById('bkgEmail').value;
        const phone = document.getElementById('bkgPhone').value;
        const date = document.getElementById('bkgDate').value;
        const travelers = parseInt(document.getElementById('bkgTravelers').value) || 1;
        const requests = document.getElementById('bkgRequests').value;

        let user = WayfareState.getCurrentUser();
        if (!user) {
            user = { name: `${firstName} ${lastName}`, email: email, role: 'user' };
            WayfareState.setCurrentUser(user);
        }

        const booking = WayfareState.addBooking({
            user_email: email,
            first_name: firstName,
            last_name: lastName,
            phone: phone,
            destination: pkgName,
            package_id: pkgId,
            date: date,
            travelers: travelers,
            special_requests: requests,
            status: 'Pending',
            total_amount: 150000 * travelers
        });

        window.closeBookingModal();
        window.location.href = `payment.html?id=${booking.id}`;
    };

    function escapeHTML(str) {
        if (!str) return '';
        return String(str).replace(/[&<>"']/g, function (m) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        WayfareState.updateHeaderNav();
    });
})();
