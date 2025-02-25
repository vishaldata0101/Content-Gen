$(function () {

  var activeIndex = $('.active-btn').index(),
      $contentlis = $('.tabsContent li'),
      $tabslis = $('.tabsButtons li');
  
  // Show content of active tab on loads
  $contentlis.eq(activeIndex).show();

  $('.tabsButtons').on('click', 'li', function (e) {
    var $current = $(e.currentTarget),
        index = $current.index();
    
    $tabslis.removeClass('active-btn');
    $current.addClass('active-btn');
    $contentlis.hide().eq(index).show();
	 });
});

