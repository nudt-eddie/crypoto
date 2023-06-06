# crypoto
（1）Server使用RSA算法生成公私钥对，并将公钥发送给client。 （2）Client随机产生比特串（我们可以自己输入），作为对称加密DES的会话密钥；并使用Bob的公钥加密这个比特串。 （3）Server收到Client加密的信息，使用自己的私钥解密，可得会话密钥。 （4）Client和Server使用对称算法加密通信内容（自己的姓名和学号）。 （5）可验证自动生成的密钥和加解密正确的结果。 （6）采用Socket编程建立Client和Server的通信连接。
