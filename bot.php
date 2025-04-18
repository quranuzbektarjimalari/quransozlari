<?php
$API_KEY = '7589991668:AAFHrbdRquQqBlPb6ig7ynBBcIa_T2nSBdM';
$bot_url = 'https://api.telegram.org/bot'.$API_KEY.'/';
$chat_id = ''; // Bu yerga foydalanuvchi yoki kanalning chat ID'sini qo'ying

function getUpdates(){
    global $bot_url;
    $updates = file_get_contents($bot_url . 'getUpdates');
    return json_decode($updates, true);
}

function sendMessage($chat_id, $message){
    global $bot_url;
    $url = $bot_url . "sendMessage?chat_id=" . $chat_id . "&text=" . urlencode($message);
    file_get_contents($url);
}

function downloadAudio($url){
    $audio_content = file_get_contents($url);
    $file_name = 'audio_' . time() . '.mp3';
    file_put_contents($file_name, $audio_content);
    return $file_name;
}

function handleMessage($update){
    if (isset($update['message']['text'])){
        $message = $update['message']['text'];
        $chat_id = $update['message']['chat']['id'];

        if (filter_var($message, FILTER_VALIDATE_URL)){
            $audio_file = downloadAudio($message);
            sendMessage($chat_id, "Audio faylni tayyorlayapman...");
            // Faylni yuborish
            sendAudio($chat_id, $audio_file);
        } else {
            sendMessage($chat_id, "Iltimos, audio fayl URL manzilini yuboring.");
        }
    }
}

function sendAudio($chat_id, $file){
    global $bot_url;
    $url = $bot_url . "sendAudio?chat_id=" . $chat_id;
    $post_data = array('chat_id' => $chat_id, 'audio' => new CURLFile($file));
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
    curl_exec($ch);
    curl_close($ch);
}

// Botni doimiy ishlatish
$updates = getUpdates();
foreach ($updates['result'] as $update){
    handleMessage($update);
}
?>
