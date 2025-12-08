# oil-price-hk

<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<div>{message}</div>
<script>
    const {createApp, ref} = Vue
    createApp({
        setup(){
            const weekday = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
            const d = new Date()
            // const message = ref('hello vue!')
            const message = ref(weekday[d.getDay()])
            return {
                message
            }
        }
    }).mount('#app')
</script>


<!-- last_update_time start -->
<!-- last_update_time end -->

Daily oil price info from hong kong consumer council

## Today Oil Info

<!-- today_s_info start -->
<!-- today_s_info end -->

## Tomorrow Oil Info
<!-- tomorrow_s_info start -->
<!-- tomorrow_s_info end -->

## Overmorrow Oil Info
<!-- overmorrow_s_info start -->
<!-- overmorrow_s_info end -->

