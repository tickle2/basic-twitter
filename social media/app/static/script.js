$(document).ready(function() {
    $('.like-btn').on('click', function(e) {
      e.preventDefault();
      var $this = $(this);
      var heartIcon = $this.find('i');
      var postId = $this.closest('.tweet-card').data('post-id');
  
      // Send POST request to /likes with post_id
      $.ajax({
        type: 'POST',
        url: '/likes',
        data: JSON.stringify({ post_id: postId }),
        contentType: 'application/json',
        success: function(response) {
          // Toggle the heart icon
          if (heartIcon.hasClass('fa-regular')) {
            heartIcon.removeClass('fa-regular').addClass('fa-solid');
          } else {
            heartIcon.removeClass('fa-solid').addClass('fa-regular');
          }
        },
        error: function(error) {
          console.log('Error:', error);
        }
      });
    });
  });
  