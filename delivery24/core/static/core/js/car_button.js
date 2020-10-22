$('#car_type input:radio').addClass('input_hidden');
$('#car_type label').click(function() {
$(this).addClass('selected').siblings().removeClass('selected');
});
