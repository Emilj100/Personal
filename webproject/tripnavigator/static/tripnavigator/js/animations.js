// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Select all elements that should animate on scroll
  const animateElements = document.querySelectorAll('.scroll-animate');
  
  // Create an IntersectionObserver to trigger animations when elements are in view
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      // If the element is visible, add the 'animate' class to trigger its animation
      if (entry.isIntersecting) {
        entry.target.classList.add('animate');
        // Stop observing the element once the animation has been triggered
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.2  // Trigger when 20% of the element is visible
  });
  
  // Start observing each animation element
  animateElements.forEach(el => observer.observe(el));
});
