var re = /add-to-cart-in-cart\d+/;
$("form[class^='add-to-cart-in-cart']").each(function(i, el){
    $('.' + el.getAttribute('class')).on('submit', function(e){
        e.preventDefault();
        var product_id = $(this).find('button').data('product');
        var cart_item_id = $(this).find('button').data('cart');
        var cart_count = $('#cart_count');
        var size = $(this).find('input[name=size]').val();
        var color = $(this).find('input[name=color]').val();
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
                var quantity = parseInt($(`input[name=quantity${cart_item_id}]`).val());
                $(`input[name=quantity${cart_item_id}]`).val(quantity + 1);
                console.log(res);
            }
        })
    })
});

