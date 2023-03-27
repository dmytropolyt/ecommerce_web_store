// some scripts

// jquery ready start
$(document).ready(function() {
	// jQuery code


    /* ///////////////////////////////////////

    THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
    For sliders, interactions and other

    */ ///////////////////////////////////////
    

	//////////////////////// Prevent closing from click inside dropdown
    $(document).on('click', '.dropdown-menu', function (e) {
      e.stopPropagation();
    });


    $('.js-check :radio').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');

        } else {
            item.removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });


    $('.js-check :checkbox').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');
        } else {
            $(this).closest('.js-check').removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });



	//////////////////////// Bootstrap tooltip
	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
		$('[data-toggle="tooltip"]').tooltip()
	} // end if




    
}); 
// jquery end

setTimeout(function(){
    $('#message').fadeOut('slow')
}, 4000);

$('.owl-carousel').owlCarousel({
    items: 4,
    margin: 10,
    responsiveClass: true,
    autoWidth: true,
    slideBy: 4,
    dotsEach: 1,
    responsive:{
        0:{
            items:1
        },
        600:{
            items:2
        },
        1000:{
            items:4
        }
    }
});

$('.add-to-wishlist').on('click', function(){
    var product_id = $(this).data('product');
    var vm = $(this);
    $.ajax({
        url: "/store/add-wishlist/",
        method: 'post',
        data:{
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            product: product_id
        },
        dataType: 'json',
        success: function(res){
            if (res.bool == true){
                vm.addClass('added-to-wishlist');
            } else {
                vm.removeClass('added-to-wishlist');
            }

            if (res.bool == true && vm.text()){
                vm.find('span').text('In wishlist');
            } else if (res.bool == false && vm.text()){
                vm.find('span').text('Add to wishlist');
            }
            console.log(vm, res);
        }
    })
});

$('#add-to-cart').on('submit', function(e){
    e.preventDefault();
    var product_id = $('.add-to-cart').data('product');
    var cart_count = $('#cart_count');
    var size = $('#product-size').val();
    var color = $('#product-color').val();
    $.ajax({
        url: `/cart/add-cart/${product_id}/`,
        method: 'post',
        data:{
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            product_id: product_id,
            color: color,
            size: size
        },
        dataType: 'json',
        success: function(res){
            cart_count.text(res['cart_items_count']);
            console.log(res);
        }
    })
});

function addDialCode(form){
    $('#id_phone_number').val($('.iti__selected-dial-code').text() + $('#id_phone_number').val());
    return true;
};
