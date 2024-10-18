import { NextResponse } from 'next/server'

// Sử dụng biến môi trường cho URL và API Key để dễ dàng cấu hình và bảo mật
const AUTH_BASE_URL = process.env.AUTH_BASE_URL || 'http://localhost:8000/auth'
const API_KEY = process.env.API_KEY || '123456'
const URL_LOGIN = '/dang-nhap'
// Hàm chung để thực hiện các yêu cầu HTTP
async function fetchFromAuth(endpoint, method = 'GET', body = null, headers = {}) {
    try {
        const response = await fetch(`${AUTH_BASE_URL}/${endpoint}`, {
            method,
            headers: {
                'X-Api-Key': API_KEY,
                'Content-Type': 'application/json',
                ...headers,
            },
            cache: 'no-cache',
            body: body ? JSON.stringify(body) : null,
        })
        const data = await response.json()
        return data
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error)
        return { status: 500 }
    }
}

// Hàm lấy token mới
async function getRefreshToken(refreshToken) {
    return await fetchFromAuth('refresh-token', 'POST', { refreshToken })
}

// Hàm lấy thông tin người dùng
async function getProfile(token) {
    return await fetchFromAuth('profile', 'GET', null, {
        'Authorization': `Bearer ${token}`
    })
}

// Hàm thiết lập token mới và chuyển hướng
function setNewTokenAndRedirect(accessToken, refreshToken, newUrl, request) {
    const response = NextResponse.redirect(new URL(newUrl, request.url), {
        headers: {
            'Set-Cookie': [
                `token=${accessToken}; HttpOnly; Path=/; Secure; SameSite=Strict`,
                `refreshToken=${refreshToken}; HttpOnly; Path=/; Secure; SameSite=Strict`
            ]
        }
    })
    return response
}

// Hàm xóa token
function deleteTokens(response) {
    response.cookies.delete('token')
    response.cookies.delete('refreshToken')
    return response
}

// Hàm kiểm tra và làm mới token nếu cần
async function authenticate(request) {
    const token = request.cookies.get('token')?.value
    const refreshToken = request.cookies.get('refreshToken')?.value

    if (!token && !refreshToken) {
        return { isAuthenticated: false }
    }

    // Kiểm tra token hiện tại
    if (token) {
        const profile = await getProfile(token)
        if (profile.status === 200) {
            return { isAuthenticated: true }
        }
    }

    // Nếu token không hợp lệ, thử làm mới
    if (refreshToken) {
        const refreshData = await getRefreshToken(refreshToken)
        if (refreshData.status === 200 && refreshData.data) {
            const { accessToken, refreshToken: newRefreshToken } = refreshData.data
            return {
                isAuthenticated: true,
                accessToken: accessToken,
                refreshToken: newRefreshToken
            }
        }
    }

    return { isAuthenticated: false }
}

export async function middleware(request) {
    const pathname = request.nextUrl.pathname

    // Định nghĩa các route cần bảo vệ
    const protectedRoutes = ['/hoi-dap']
    const authRoutes = ['/dang-nhap']

    if (authRoutes.includes(pathname)) {
        const { isAuthenticated, accessToken, refreshToken } = await authenticate(request)

        if (accessToken && refreshToken) {
            // Nếu làm mới token thành công, thiết lập cookie mới và chuyển hướng
            return setNewTokenAndRedirect(accessToken, refreshToken, '/', request)
        }

        if (isAuthenticated === true) {
            // Nếu đã đăng nhập, chuyển hướng về trang chủ
            return NextResponse.redirect(new URL('/', request.url))
        }


        // Nếu không xác thực, xóa cookie và tiếp tục
        const response = NextResponse.next()
        deleteTokens(response)
        return response
    }

    if (protectedRoutes.includes(pathname)) {
        const { isAuthenticated, accessToken, refreshToken } = await authenticate(request)

        if (accessToken && refreshToken) {
            // Nếu làm mới token thành công, thiết lập cookie mới và chuyển hướng đến trang hiện tại
            return setNewTokenAndRedirect(accessToken, refreshToken, pathname, request)
        }

        if (!isAuthenticated) {
            // Nếu chưa xác thực, chuyển hướng đến trang đăng nhập
            return NextResponse.redirect(new URL(URL_LOGIN, request.url))
        }

    }

    return NextResponse.next()
}

export const config = {
    matcher: [
        // Loại trừ các đường dẫn không cần middleware
        "/((?!api|_next/static|_next/image|favicon.ico).*)",
    ],
}
