public class CuentaBancaria {
    private String titular;
    private double saldo;
    private int numeroCuenta;

    public CuentaBancaria(String titular, double saldoInicial, int numeroCuenta) {
        this.titular = titular;
        this.saldo = saldoInicial;
        this.numeroCuenta = numeroCuenta;
    }

    public void depositar(double cantidad) {
        if (cantidad > 0) saldo += cantidad;
    }

    public void retirar(double cantidad) {
        if (cantidad > 0 && saldo >= cantidad) saldo -= cantidad;
    }

    public void mostrarResumen() {
        System.out.println("Titular: " + titular + ", Saldo: " + saldo);
    }

    public void transferir(CuentaBancaria destino, double cantidad) {
        if (saldo >= cantidad && cantidad > 0) {
            this.retirar(cantidad);
            destino.depositar(cantidad);
        }
    }
}
