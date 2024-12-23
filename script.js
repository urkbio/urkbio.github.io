// 页面加载完成后的动画效果
document.addEventListener('DOMContentLoaded', function() {
    // 添加渐入动画
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 200 * (index + 1));
    });

    // 添加头像hover效果
    const profileImg = document.querySelector('.profile-img img');
    if (profileImg) {
        profileImg.addEventListener('mouseover', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.3s ease';
        });

        profileImg.addEventListener('mouseout', function() {
            this.style.transform = 'scale(1)';
        });
    }
});
