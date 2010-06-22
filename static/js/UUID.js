/*
---
description: enerate an UUID as per RFC 4122 section 4.4

license: MIT-style

authors:
- Wijnand Modderman

requires:
 core/1.2.4:
  - Native.Class 
  - Native.Hash

provides: [Math.uuid, Math.uuidCompact]

...
*/

(function() {
    var uuidChars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
    var uuidFixed = new Hash({8: '-', 13: '-', 14: '4', 18: '-', 23: '-'});

    Math.uuid = function() {
        var uuid = new Array(36), a = 0, r;
        for (var i = 0; i < 36; ++i) {
            if (uuidFixed.has(i)) {
                uuid[i] = uuidFixed[i];
            } else {
                if (a < 0x02) a = 0x2000000 + (Math.random() * 0x1000000)|0;
                r = a & 0x0f;
                a = a >> 0x4;
                uuid[i] = uuidChars[(i == 19) ? (r & 0x3) | 0x8 : r];
            }
        }
        return uuid.join('');
    };

    Math.uuidCompact = function(size, base) {
        size = size || 32;
        base = base || uuidChars.length;
        var uuid = new Array(size);
        for (var i = 0; i < size; ++i) {
            uuid[i] = uuidChars[(Math.random() * base)|0];
        }
        return uuid.join('');
    }
})();

