# Minimal pure-Python LZO1X decompressor (API-compatible with python-lzo's decompress(src, header, buflen)).
# Written from the public LZO1X format (same structure as the Linux kernel's lzo1x_decompress_safe).
def decompress(src, header=False, buflen=0):
    src = bytes(src)
    ip = 0; out = bytearray(); n = len(src)
    def copy_match(m_pos, t):
        # copy t+2 bytes from out[m_pos:], overlapping allowed
        for _ in range(t + 2):
            if m_pos < 0: raise ValueError('lzo: bad match offset')
            out.append(out[m_pos]); m_pos += 1
    t = src[ip]
    state_first_literal = False
    if t > 17:
        ip += 1; t -= 17
        if t < 4:
            out += src[ip:ip+t]; ip += t; t = src[ip]; ip += 1
            # continue in match loop with next instruction in t
            goto = 'match'
        else:
            out += src[ip:ip+t]; ip += t
            goto = 'first_literal_run'
    else:
        goto = 'literal'
    while True:
        if goto == 'literal':
            t = src[ip]; ip += 1
            if t >= 16:
                goto = 'match'
            else:
                if t == 0:
                    while src[ip] == 0: t += 255; ip += 1
                    t += 15 + src[ip]; ip += 1
                out += src[ip:ip+t+3]; ip += t + 3
                goto = 'first_literal_run'
                continue
        if goto == 'first_literal_run':
            t = src[ip]; ip += 1
            if t >= 16:
                goto = 'match'
            else:
                m_pos = len(out) - (1 + 0x0800) - (t >> 2) - (src[ip] << 2); ip += 1
                copy_match(m_pos, 1)   # 3 bytes
                # match_done
                t = src[ip-2] & 3
                if t == 0:
                    goto = 'literal'; continue
                out += src[ip:ip+t]; ip += t; t = src[ip]; ip += 1
                goto = 'match'
        # inner match loop
        while True:
            if t >= 64:
                m_pos = len(out) - 1 - ((t >> 2) & 7) - (src[ip] << 3); ip += 1
                copy_match(m_pos, (t >> 5) - 1)
            elif t >= 32:
                t &= 31
                if t == 0:
                    while src[ip] == 0: t += 255; ip += 1
                    t += 31 + src[ip]; ip += 1
                m_pos = len(out) - 1 - ((src[ip] >> 2) + (src[ip+1] << 6)); ip += 2
                copy_match(m_pos, t)
            elif t >= 16:
                m_pos = len(out) - ((t & 8) << 11)
                t &= 7
                if t == 0:
                    while src[ip] == 0: t += 255; ip += 1
                    t += 7 + src[ip]; ip += 1
                m_pos -= (src[ip] >> 2) + (src[ip+1] << 6); ip += 2
                if m_pos == len(out):
                    return bytes(out)          # end-of-stream marker
                m_pos -= 0x4000
                copy_match(m_pos, t)
            else:
                m_pos = len(out) - 1 - (t >> 2) - (src[ip] << 2); ip += 1
                copy_match(m_pos, 0)           # 2 bytes
            # match_done
            t = src[ip-2] & 3
            if t == 0:
                goto = 'literal'; break
            out += src[ip:ip+t]; ip += t; t = src[ip]; ip += 1
        if ip >= n and len(out) >= buflen: return bytes(out)
