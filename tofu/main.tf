terraform {
  required_providers {
    libvirt = {
      source = "registry.terraform.io/dmacvicar/libvirt"
      version = "0.9.8"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

# Том для VM (создаём пустой, потом вручную скопируем базовый образ)
resource "libvirt_volume" "vm_disk" {
  name     = "pet-project-vm.qcow2"
  pool     = "default"
  capacity = 10 * 1024 * 1024 * 1024
}

# Cloud-init
resource "libvirt_cloudinit_disk" "cloudinit" {
  name      = "pet-project-cloudinit.iso"
  user_data = <<-EOF
    #cloud-config
    hostname: pet-project
    users:
      - name: sre
        sudo: ALL=(ALL) NOPASSWD:ALL
        shell: /bin/bash
        ssh_authorized_keys:
          - ${file("~/.ssh/id_ed25519.pub")}
    package_update: true
    runcmd:
      - systemctl enable --now docker
  EOF
  meta_data = <<-EOF
    instance-id: pet-project
    local-hostname: pet-project
  EOF
}

# VM
resource "libvirt_domain" "pet_project" {
  name   = "pet-project"
  memory = "2048"
  vcpu   = 2
  type   = "kvm"

  os = {
    type = "hvm"
  }
}
